from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
from typing import Optional
from pathlib import Path
from generate_poster import generate_poster
from enhance_prompt import enhance_prompt
from add_logo import add_logo_to_poster
from watermark import add_watermark
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import models
import database
from typing import List
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Initialize FastAPI app
app = FastAPI(title="AI Poster Generator API",
             description="API for generating posters with AI",
             version="1.0.0")

# Configuration
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "static" / "posters"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Templates for HTML responses
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main HTML interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/generate")
    
async def generate_poster_endpoint(
    prompt: str = Form(...),
    logo_position: str = Form("bottom-right"),
    logo: Optional[UploadFile] = File(None)
):
    try:
        print(">>> Starting generation with prompt:", prompt)

        # Step 1: Handle logo upload if provided
        logo_path = None
        if logo and logo.filename:
            filename = f"logo_{uuid.uuid4().hex}{Path(logo.filename).suffix}"
            logo_path = UPLOAD_FOLDER / filename
            with open(logo_path, "wb") as buffer:
                buffer.write(await logo.read())
            print(">>> Logo saved to:", logo_path)

        # Step 2: Enhance the prompt
        enhanced_prompt = enhance_prompt(prompt, str(logo_path) if logo_path else None)
        print(">>> Enhanced prompt:", enhanced_prompt)

        # Step 3: Generate the poster
        poster_path = generate_poster(enhanced_prompt)
        print(">>> Poster generated at:", poster_path)

        # Validate poster file
        if not poster_path or not Path(poster_path).exists():
            raise HTTPException(status_code=500, detail="Poster generation failed - file not created")
        if Path(poster_path).stat().st_size < 1000:
            raise HTTPException(status_code=500, detail="Poster generation failed - file too small")

        # Confirm it's a valid image
        try:
            from PIL import Image
            with Image.open(poster_path) as img:
                img.verify()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Poster verification failed: {str(e)}")

        # Step 4: Add logo to poster if applicable
        if logo_path and logo_path.exists():
            try:
                poster_path = add_logo_to_poster(poster_path, str(logo_path), logo_position)
                print(">>> Logo added to poster:", poster_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to add logo: {str(e)}")

        # Step 5: Add watermark
        try:
            final_path = add_watermark(poster_path)
            print(">>> Final poster with watermark at:", final_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add watermark: {str(e)}")

        # Clean up uploaded logo
        if logo_path and logo_path.exists():
            logo_path.unlink(missing_ok=True)

        return JSONResponse({
            "success": True,
            "poster_url": f"/static/posters/{Path(final_path).name}",
            "enhanced_prompt": enhanced_prompt
        })

    except HTTPException:
        raise
    except Exception as e:
        print(">>> Unexpected error:", str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")




@app.post("/images/")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check and delete old images if more than 10
    image_count = db.query(models.Image).count()
    if image_count >= 10:
        # Delete oldest images to maintain only 9
        oldest_images = db.query(models.Image).order_by(models.Image.created_at).limit(image_count - 9).all()
        for img in oldest_images:
            db.delete(img)
        db.commit()
    
    # Read image data
    image_data = await file.read()
    
    # Store new image
    db_image = models.Image(
        name=file.filename,
        content_type=file.content_type,
        data=image_data,
        created_at=datetime.utcnow()
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return {"id": db_image.id, "name": db_image.name}

@app.get("/images/", response_model=List[dict])
async def get_images(db: Session = Depends(get_db)):
    images = db.query(models.Image).order_by(models.Image.created_at.desc()).all()
    return [{"id": img.id, "name": img.name} for img in images]

@app.get("/images/{image_id}")
async def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image.data, media_type=image.content_type)


@app.get("/api/posters/{filename}")
async def serve_poster(filename: str):
    """Serve generated poster files"""
    poster_path = UPLOAD_FOLDER / filename
    if not poster_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Poster not found"
        )
    return FileResponse(poster_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )