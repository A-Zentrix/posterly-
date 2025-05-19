from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles 
from pydantic_settings import BaseSettings
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
import pymysql
import bcrypt
import re
import os
from contextlib import contextmanager
<<<<<<< HEAD
from starlette.middleware.sessions import SessionMiddleware
from config import Config
from typing import Optional  # Add this import

# Initialize FastAPI app
app = FastAPI()
=======
from flask import Flask, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests
app = Flask(__name__)
app.config.from_object(Config)
>>>>>>> 38ed2c82c12f6e1c85783f1bb1afccf1f47a6564

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=Config.SECRET_KEY,
    session_cookie="session"
)

# Configure CSRF protection
class CsrfSettings(BaseSettings):
    secret_key: str = Config.SECRET_KEY
    cookie_samesite: str = "lax"
    cookie_secure: bool = False  # Set to True in production with HTTPS

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# Configure templates and static files
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")

templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Database connection helpers
@contextmanager
def get_db_connection():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        db=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        finally:
            cursor.close()

# Helper functions
def is_valid_email(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.match(regex, email)

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if 'loggedin' in request.session:
        return f"Welcome back, {request.session['username']}! <a href='/logout'>Logout</a>"
    return RedirectResponse(url="/login")

@app.get("/login")
async def login_page(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    return templates.TemplateResponse("login.html", {
        "request": request,
        "csrf_token": csrf_token
    })

@app.post("/login")
async def login(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
    email: str = Form(...),
    password: str = Form(...),
    remember: Optional[str] = Form(None)
):
    try:
        csrf_protect.validate_csrf(request)
    except CsrfProtectError:
        raise HTTPException(status_code=403, detail="CSRF token validation failed")

    password = password.encode('utf-8')
    message = ''
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
                request.session['loggedin'] = True
                request.session['userid'] = user['id']
                request.session['username'] = user['username']
                request.session['email'] = user['email']
                
                if remember:
                    request.session.setdefault("permanent", True)
                
                return RedirectResponse(url="/", status_code=303)
            else:
                message = 'Invalid email/password combination'
    except Exception as e:
        message = 'Database error occurred'

    csrf_token = csrf_protect.generate_csrf()
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": message,
        "csrf_token": csrf_token
    })

@app.get("/register")
async def register_page(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    return templates.TemplateResponse("login.html", {
        "request": request,
        "csrf_token": csrf_token,
        "register_active": True
    })

@app.post("/register")
async def register(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    try:
        csrf_protect.validate_csrf(request)
    except CsrfProtectError:
        raise HTTPException(status_code=403, detail="CSRF token validation failed")

<<<<<<< HEAD
=======

@app.route('/register', methods=['GET', 'POST'])
def register():
>>>>>>> 38ed2c82c12f6e1c85783f1bb1afccf1f47a6564
    message = ''
    
    if password != confirm_password:
        message = 'Passwords do not match!'
    elif not is_valid_email(email):
        message = 'Invalid email address!'
    else:
        password = password.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                account = cursor.fetchone()
                
                if account:
                    message = 'Account already exists!'
                else:
                    cursor.execute(
                        'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                        (username, email, hashed)
                    )
                    message = 'You have successfully registered!'
                    return RedirectResponse(url="/login", status_code=303)
        except Exception as e:
            message = 'Database error occurred'

    csrf_token = csrf_protect.generate_csrf()
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": message,
        "csrf_token": csrf_token,
        "register_active": True
    })

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/forgot-password")
async def forgot_password_page(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    return templates.TemplateResponse("login.html", {
        "request": request,
        "csrf_token": csrf_token
    })

@app.post("/forgot-password")
async def forgot_password(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
    email: str = Form(...)
):
    try:
        csrf_protect.validate_csrf(request)
    except CsrfProtectError:
        raise HTTPException(status_code=403, detail="CSRF token validation failed")

    try:
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if user:
                request.session['message'] = 'Password reset link has been sent to your email'
                return RedirectResponse(url="/login", status_code=303)
            else:
                request.session['message'] = 'Email not found'
    except Exception as e:
        request.session['message'] = 'Database error occurred'

    return RedirectResponse(url="/login", status_code=303)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)