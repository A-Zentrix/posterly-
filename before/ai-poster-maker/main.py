# main.py (entry point)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional
from generate_poster import generate_poster
from enhance_prompt import enhance_prompt
from add_logo import add_logo_to_poster
from watermark import add_watermark
import uuid

app = FastAPI()

# Configuration
UPLOAD_FOLDER = 'static/posters'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return {"message": "Poster Generator API"}

@app.post("/generate")
async def generate(
    prompt: str = Form(...),
    logo_position: str = Form("bottom-right"),
    logo: Optional[UploadFile] = File(None)
):
    try:
        # Handle logo upload
        logo_path = None
        if logo and logo.filename:
            filename = f"{uuid.uuid4().hex}_{logo.filename}"
            logo_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(logo_path, "wb") as buffer:
                buffer.write(await logo.read())
        
        # Enhance prompt if needed
        enhanced_prompt = enhance_prompt(prompt) if prompt else ""
        
        # Generate poster
        poster_path = generate_poster(enhanced_prompt or prompt)
        if not poster_path:
            raise HTTPException(status_code=500, detail="Failed to generate poster")
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            poster_path = add_logo_to_poster(poster_path, logo_path, logo_position)
        
        # Add watermark
        final_path = add_watermark(poster_path)
        if not final_path:
            raise HTTPException(status_code=500, detail="Failed to add watermark")
        
        # Return relative URL for the generated poster
        poster_url = f"/{final_path}"
        
        return JSONResponse({
            'success': True,
            'poster_url': poster_url,
            'enhanced_prompt': enhanced_prompt
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posters/{filename}")
async def serve_poster(filename: str):
    poster_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(poster_path):
        raise HTTPException(status_code=404, detail="Poster not found")
    return FileResponse(poster_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)