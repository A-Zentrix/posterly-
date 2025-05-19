import os
import mimetypes
import uuid
from google import genai
from google.genai import types

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)

def generate_poster(prompt: str) -> str:
    api_key = "AIzaSyB9_W_CWeAPD1E_y7fxZxp8ELtgUikq5X4" # fallback key
    client = genai.Client(api_key=api_key)

    model = "gemini-2.0-flash-exp-image-generation"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_modalities=["image", "text"],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue

        part = chunk.candidates[0].content.parts[0]
        if part.inline_data:
            file_id = uuid.uuid4()
            file_name = f"poster_{file_id}"
            print(">> Gemini response part:", part)


            inline_data = part.inline_data
            file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".jpg"
            final_filename = f"{file_name}{file_extension}"

            save_binary_file(final_filename, inline_data.data)

            return final_filename  # return filename

    return "no image was generated"  # If no image was generated

if __name__ == "__main__":
    example_prompt = (
        "Create a poster featuring a stylized portrait of A.P.J. Abdul Kalam. "
        "Emphasize his wise gaze and distinct hairstyle. "
        "Use a warm, golden-orange color palette inspired by the background, "
        "transitioning to a slightly darker shade towards the edges. "
        "Incorporate subtle textures resembling parchment or old paper for a timeless feel. "
        "The overall design should evoke a sense of wisdom, vision, and national pride. "
        "Include a minimalist quote like 'Dream, Dream, Dream' or 'Great dreams of great dreamers are always transcended.' "
        "Attach a logo with a text brand name (Azentrix)."
    )
    output_file = generate_poster(example_prompt)
    if output_file:
        print(f"✅ Poster saved as: {output_file}")
    else:
        print("⚠️ Failed to generate poster.")
