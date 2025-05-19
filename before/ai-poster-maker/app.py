from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from generate_poster import generate_poster
from enhance_prompt import enhance_prompt
from add_logo import add_logo_to_poster
from watermark import add_watermark

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/posters'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get data from request
        prompt = request.form.get('prompt')
        logo_position = request.form.get('logo_position', 'bottom-right')
        
        # Check if logo was uploaded
        logo_path = None
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file.filename != '':
                filename = secure_filename(logo_file.filename)
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                logo_file.save(logo_path)
        
        # Enhance prompt if needed
        enhanced_prompt = enhance_prompt(prompt) if prompt else ""
        
        # Generate poster
        poster_path = generate_poster(enhanced_prompt or prompt)
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            poster_path = add_logo_to_poster(poster_path, logo_path, logo_position)
        
        # Add watermark
        final_path = add_watermark(poster_path)
        
        return jsonify({
            'success': True,
            'poster_url': final_path,
            'enhanced_prompt': enhanced_prompt
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/posters/<filename>')
def serve_poster(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)