class Config:
<<<<<<< HEAD
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bed329f95b06bff416af489eb2fa9debae59f2a6ebb49a9a99700d9365a68949'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'arfeen@6106'
    MYSQL_DB = 'login_system'
    MYSQL_CURSORCLASS = 'DictCursor'
    MYSQL_CHARSET = 'utf8mb4'
    SECURE_COOKIES = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'lax'
=======
    # ... existing config ...
    
    # Facebook OAuth
    FACEBOOK_CLIENT_ID = 'your-facebook-app-id'
    FACEBOOK_CLIENT_SECRET = 'your-facebook-app-secret'
    
    # Google OAuth
    GOOGLE_CLIENT_ID = 'your-google-client-id'
    GOOGLE_CLIENT_SECRET = 'your-google-client-secret'
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID = 'your-linkedin-client-id'
    LINKEDIN_CLIENT_SECRET = 'your-linkedin-client-secret'
>>>>>>> 38ed2c82c12f6e1c85783f1bb1afccf1f47a6564
