from PIL import Image
import colorsys
from collections import Counter
import webcolors

def get_dominant_colors(image_path, num_colors=3):
    """Extract dominant colors from an image"""
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    # Resize for faster processing (optional)
    img = img.resize((100, 100))
    
    # Get colors
    pixels = list(img.getdata())
    color_counts = Counter(pixels)
    
    # Get most common colors
    dominant_colors = color_counts.most_common(num_colors)
    
    return [color[0] for color in dominant_colors]

def rgb_to_names(rgb_tuple):
    """Convert RGB to color names"""
    try:
        color_name = webcolors.rgb_to_name(rgb_tuple)
        return color_name
    except ValueError:
        # Find closest color name
        min_colors = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - rgb_tuple[0]) ** 2
            gd = (g_c - rgb_tuple[1]) ** 2
            bd = (b_c - rgb_tuple[2]) ** 2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

def analyze_logo_colors(logo_path):
    """Analyze logo colors and return descriptive text"""
    try:
        colors = get_dominant_colors(logo_path)
        color_names = [rgb_to_names(color) for color in colors]
        
        # Create descriptive text
        if len(color_names) == 1:
            return f"using a {color_names[0]} color scheme that matches the logo"
        else:
            primary = color_names[0]
            secondary = ", ".join(color_names[1:-1])
            last = color_names[-1]
            return f"using a color palette dominated by {primary}, with accents of {secondary} and {last} to complement the logo"
    
    except Exception as e:
        print(f"Color analysis error: {e}")
        return ""