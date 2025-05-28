from flask import Flask, request, jsonify, render_template
import os
import meshcapade
from werkzeug.utils import secure_filename
from meshcapade.exceptions import APIError, TimeoutError, ValidationError

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-avatar', methods=['POST'])
def create_avatar():
    try:
        # Check if image file is present in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg'}), 400

        # Get other parameters from form data
        name = request.form.get('name')
        gender = request.form.get('gender')
        api_key = request.form.get('api_key')
        
        # Optional parameters
        height = request.form.get('height')
        weight = request.form.get('weight')

        # Validate required parameters
        if not all([name, gender, api_key]):
            return jsonify({'error': 'Missing required parameters: name, gender, and api_key are required'}), 400

        # Validate gender
        if gender not in ['male', 'female']:
            return jsonify({'error': 'Gender must be either "male" or "female"'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Initialize MeshCapade SDK with the provided API key
        meshcapade.set_api_key(api_key)
        avatar = meshcapade.Avatar()

        # Set required parameters
        avatar.name = name
        avatar.gender = gender

        # Set optional parameters if provided
        if height:
            try:
                avatar.height = int(height)
            except ValueError:
                return jsonify({'error': 'Height must be a valid integer'}), 400

        if weight:
            try:
                avatar.weight = int(weight)
            except ValueError:
                return jsonify({'error': 'Weight must be a valid integer'}), 400

        # Create avatar from image
        avatar_id = avatar.create_avatar_from_image(image_paths=[filepath])

        # Clean up - remove uploaded file
        os.remove(filepath)

        return jsonify({
            'message': 'Avatar creation initiated successfully',
            'avatar_id': avatar_id
        }), 201

    except ValidationError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except APIError as e:
        return jsonify({'error': f'API error: {str(e)}'}), 500
    except TimeoutError as e:
        return jsonify({'error': f'Timeout error: {str(e)}'}), 504
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 