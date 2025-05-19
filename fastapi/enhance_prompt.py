import google.generativeai as genai
import os
from typing import Optional
from logo_color_analysis import analyze_logo_colors  # Import the color analysis function
from fastapi import HTTPException

# Configure Gemini AI with error handling
try:
    genai.configure(api_key="AIzaSyA_LfnvKFq5dLFKYpArkIXwjxqgiZaFD1s")
except Exception as e:
    raise RuntimeError(f"Failed to configure Gemini AI: {str(e)}")

# Model configuration with type hints
GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize model with error handling
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=GENERATION_CONFIG,
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize GenerativeModel: {str(e)}")

def enhance_prompt(raw_prompt: str, logo_path: Optional[str] = None) -> str:
    """
    Enhance the user's prompt with creative details and optional logo color analysis.
    
    Args:
        raw_prompt: The original user prompt
        logo_path: Optional path to uploaded logo for color analysis
        
    Returns:
        Enhanced creative prompt
        
    Raises:
        HTTPException: If prompt generation fails
    """
    try:
        # Analyze logo colors if provided
        color_description = ""
        if logo_path and os.path.exists(logo_path):
            color_description = analyze_logo_colors(logo_path)
        
        # Combine with original prompt
        combined_prompt = f"{raw_prompt} {color_description}".strip()
        
        # System instruction for the AI
        system_instruction = (
            "You are a professional poster designer. Transform this brief into a vivid, "
            "detailed visual description suitable for image generation. Focus on:\n"
            "- Composition and layout\n"
            "- Color schemes and lighting\n"
            "- Emotional tone and style\n"
            "- Key visual elements\n"
            "Keep it concise (40-60 words)."
        )
        
        # Generate enhanced prompt
        response = model.generate_content([
            system_instruction,
            f"Client brief: {combined_prompt}",
            "Design description:"
        ])
        
        # Validate and return response
        if not response.text:
            raise ValueError("Empty response from AI model")
            
        return response.text.strip()
        
    except Exception as e:
        error_msg = f"Prompt enhancement failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)