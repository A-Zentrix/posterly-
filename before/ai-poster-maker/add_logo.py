from PIL import Image
import os
from uuid import uuid4

def add_logo_to_poster(poster_path: str, logo_path: str, position: str) -> str:
    try:
        # Open the poster and logo
        poster = Image.open(poster_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")

        # Resize the logo to fit the poster nicely
        logo_width = poster.width // 6
        aspect_ratio = logo.height / logo.width
        logo_height = int(logo_width * aspect_ratio)
        logo = logo.resize((logo_width, logo_height))

        # Decide position
        padding = 30
        if position == "top-left":
            pos = (padding, padding)
        elif position == "top-right":
            pos = (poster.width - logo.width - padding, padding)
        elif position == "bottom-left":
            pos = (padding, poster.height - logo.height - padding)
        elif position == "bottom-right":
            pos = (poster.width - logo.width - padding, poster.height - logo.height - padding)
        elif position == "center":
            pos = ((poster.width - logo.width) // 2, (poster.height - logo.height) // 2)
        else:
            pos = (padding, padding)  # default fallback

        # Paste logo on poster
        poster.paste(logo, pos, logo)

        # Save the result
        output_path = f"static/posters/with_logo_{uuid4().hex}.png"
        poster.save(output_path, format="PNG")

        return output_path

    except Exception as e:
        print(f"Error adding logo: {e}")
        return poster_path  # Return original if failed
