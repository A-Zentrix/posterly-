from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends, Response
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import uuid
import os
import logging
from typing import Optional, List

import models
import database
from generate_poster import generate_poster
from enhance_prompt import enhance_prompt
from add_logo import add_logo_to_poster
from watermark import add_watermark

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app instance
app = FastAPI(title="AI Poster Generator API",
              description="API for generating posters with AI",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = Path(__file__).parent.resolve()
UPLOAD_FOLDER = BASE_DIR / "static" / "posters"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Templates & static mount
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/generate")
async def generate_poster_endpoint(
    prompt: str = Form(...),
    logo_position: str = Form("bottom-right"),
    logo: Optional[UploadFile] = File(None)
):
    try:
        logger.info("Starting poster generation")
        
        # Step 1: Save logo if provided
        logo_path = None
        if logo and logo.filename:
            filename = f"logo_{uuid.uuid4().hex}{Path(logo.filename).suffix}"
            logo_path = UPLOAD_FOLDER / filename
            with open(logo_path, "wb") as f:
                f.write(await logo.read())
            logger.info(f"Logo saved to: {logo_path}")

        # Step 2: Enhance prompt
        enhanced_prompt = enhance_prompt(prompt, str(logo_path) if logo_path else None)
        logger.info(f"Enhanced prompt: {enhanced_prompt}")

        # Step 3: Generate poster
        poster_path = generate_poster(enhanced_prompt)
        poster_path = Path(poster_path)
        logger.info(f"Initial poster generated at: {poster_path}")

        if not poster_path.exists() or poster_path.stat().st_size < 1000:
            raise Exception("Poster generation failed or file is invalid")

        # Step 4: Add logo to poster if applicable
        if logo_path and logo_path.exists():
            poster_path = Path(add_logo_to_poster(str(poster_path), str(logo_path), logo_position))
            logger.info(f"Poster with logo at: {poster_path}")

        # Step 5: Add watermark
        final_path = Path(add_watermark(str(poster_path)))
        if not final_path.exists():
            raise Exception("Failed to add watermark")
        logger.info(f"Final watermarked poster at: {final_path}")

        # Construct URL
        poster_url = f"/static/posters/{final_path.name}"
        logger.info(f"Poster URL: {poster_url}")

        # Step 6: Clean up intermediate files
        if logo_path and logo_path.exists():
            logo_path.unlink()
        if poster_path.exists() and poster_path != final_path:
            poster_path.unlink()

        return JSONResponse({
            "success": True,
            "poster_url": poster_url,
            "enhanced_prompt": enhanced_prompt
        })

    except Exception as e:
        logger.error(f"Error generating poster: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ... (rest of your existing endpoints remain the same)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)