from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from pathlib import Path
import traceback
import time

from models.style_transfer import StyleTransferModel
from models.model_loader import ModelLoader
from models.gan_inference import GANInference
from utils.image_processing import ImageProcessor
from utils.model_utils import (
    allowed_file, 
    generate_filename, 
    create_response,
    sanitize_filename,
    validate_image_size
)

transfer_bp = Blueprint('transfer', __name__)

# Initialize models (will be done once)
model_loader = None
style_transfer_model = None
gan_inference = None

def init_models():
    """Initialize ML models"""
    global model_loader, style_transfer_model, gan_inference
    
    if model_loader is None:
        print("🔧 Initializing models...")
        model_loader = ModelLoader(current_app.config['PRETRAINED_MODELS_PATH'])
        style_transfer_model = StyleTransferModel(
            model_loader, 
            image_size=current_app.config['IMAGE_SIZE']
        )
        gan_inference = GANInference(model_loader.device)
        print("✅ Models initialized successfully")


@transfer_bp.route('/styles', methods=['GET'])
def get_styles():
    """Get available style presets"""
    styles = [
        {
            'id': 'starry_night',
            'name': 'Starry Night',
            'description': 'Van Gogh inspired swirling patterns',
            'thumbnail': '/static/styles/starry_night.jpg'
        },
        {
            'id': 'picasso',
            'name': 'Cubist',
            'description': 'Picasso-style geometric abstraction',
            'thumbnail': '/static/styles/picasso.jpg'
        },
        {
            'id': 'mosaic',
            'name': 'Mosaic',
            'description': 'Colorful mosaic tile patterns',
            'thumbnail': '/static/styles/mosaic.jpg'
        },
        {
            'id': 'wave',
            'name': 'The Great Wave',
            'description': 'Japanese woodblock print style',
            'thumbnail': '/static/styles/wave.jpg'
        },
        {
            'id': 'candy',
            'name': 'Candy',
            'description': 'Bright, colorful pop art style',
            'thumbnail': '/static/styles/candy.jpg'
        }
    ]
    
    return jsonify(create_response(
        success=True,
        message="Styles retrieved successfully",
        data={'styles': styles}
    ))


@transfer_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload an image for processing"""
    try:
        if 'file' not in request.files:
            return jsonify(create_response(
                success=False,
                message="No file provided",
                error="file_required"
            )), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify(create_response(
                success=False,
                message="No file selected",
                error="empty_filename"
            )), 400
        
        if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify(create_response(
                success=False,
                message="File type not allowed. Please upload PNG, JPG, or JPEG",
                error="invalid_file_type"
            )), 400
        
        # Generate unique filename
        filename = generate_filename(
            prefix='upload',
            extension=file.filename.rsplit('.', 1)[1].lower()
        )
        
        filepath = current_app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)
        
        # Validate file size
        is_valid, size_mb = validate_image_size(filepath)
        if not is_valid:
            filepath.unlink()  # Delete the file
            return jsonify(create_response(
                success=False,
                message=f"File too large ({size_mb:.1f}MB). Maximum size is 16MB",
                error="file_too_large"
            )), 400
        
        # Get image info
        img_info = ImageProcessor.get_image_info(filepath)
        
        return jsonify(create_response(
            success=True,
            message="File uploaded successfully",
            data={
                'filename': filename,
                'path': str(filepath),
                'info': img_info
            }
        )), 201
        
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        print(traceback.format_exc())
        return jsonify(create_response(
            success=False,
            message="Error uploading file",
            error=str(e)
        )), 500


@transfer_bp.route('/transfer', methods=['POST'])
def perform_transfer():
    """Perform style transfer on an image"""
    try:
        # Initialize models if needed
        init_models()
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'content_image' not in data or 'style_image' not in data:
            return jsonify(create_response(
                success=False,
                message="Missing required fields: content_image and style_image",
                error="missing_fields"
            )), 400
        
        content_path = Path(data['content_image'])
        style_path = Path(data['style_image'])
        
        # Validate files exist
        if not content_path.exists():
            return jsonify(create_response(
                success=False,
                message="Content image not found",
                error="content_not_found"
            )), 404
        
        if not style_path.exists():
            return jsonify(create_response(
                success=False,
                message="Style image not found",
                error="style_not_found"
            )), 404
        
        # Get parameters
        intensity = float(data.get('intensity', 1.0))
        quality = data.get('quality', 'standard')  # 'fast', 'standard', 'high'
        
        # Determine number of steps based on quality
        num_steps_map = {
            'fast': 100,
            'standard': 200,
            'high': 300
        }
        num_steps = num_steps_map.get(quality, 200)
        
        # Generate output filename
        output_filename = generate_filename(prefix='styled', extension='png')
        output_path = current_app.config['UPLOAD_FOLDER'] / output_filename
        
        print(f"🎨 Starting style transfer...")
        print(f"   Content: {content_path.name}")
        print(f"   Style: {style_path.name}")
        print(f"   Quality: {quality} ({num_steps} steps)")
        print(f"   Intensity: {intensity}")
        
        start_time = time.time()
        
        # Perform style transfer
        result_path = style_transfer_model.transfer_style(
            content_path=str(content_path),
            style_path=str(style_path),
            output_path=str(output_path),
            num_steps=num_steps,
            style_weight=int(1000000 * intensity),
            content_weight=1
        )
        
        processing_time = time.time() - start_time
        
        # Get result image info
        result_info = ImageProcessor.get_image_info(output_path)
        
        print(f"✅ Style transfer completed in {processing_time:.1f}s")
        
        return jsonify(create_response(
            success=True,
            message="Style transfer completed successfully",
            data={
                'output_image': output_filename,
                'output_path': str(output_path),
                'processing_time': f"{processing_time:.1f}s",
                'info': result_info
            }
        )), 200
        
    except Exception as e:
        print(f"Error in style transfer: {str(e)}")
        print(traceback.format_exc())
        return jsonify(create_response(
            success=False,
            message="Error performing style transfer",
            error=str(e)
        )), 500


@transfer_bp.route('/quick-transfer', methods=['POST'])
def quick_transfer():
    """Perform quick style transfer (fewer iterations)"""
    try:
        init_models()
        
        data = request.get_json()
        
        if not data or 'content_image' not in data or 'style_image' not in data:
            return jsonify(create_response(
                success=False,
                message="Missing required fields",
                error="missing_fields"
            )), 400
        
        content_path = Path(data['content_image'])
        style_path = Path(data['style_image'])
        intensity = float(data.get('intensity', 1.0))
        
        output_filename = generate_filename(prefix='quick_styled', extension='png')
        output_path = current_app.config['UPLOAD_FOLDER'] / output_filename
        
        print(f"⚡ Starting quick style transfer...")
        start_time = time.time()
        
        result_path = style_transfer_model.quick_transfer(
            content_path=str(content_path),
            style_path=str(style_path),
            output_path=str(output_path),
            intensity=intensity
        )
        
        processing_time = time.time() - start_time
        
        return jsonify(create_response(
            success=True,
            message="Quick style transfer completed",
            data={
                'output_image': output_filename,
                'output_path': str(output_path),
                'processing_time': f"{processing_time:.1f}s"
            }
        )), 200
        
    except Exception as e:
        print(f"Error in quick transfer: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="Error performing quick transfer",
            error=str(e)
        )), 500


@transfer_bp.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    """Serve an image file"""
    try:
        filepath = current_app.config['UPLOAD_FOLDER'] / filename
        
        if not filepath.exists():
            return jsonify(create_response(
                success=False,
                message="Image not found",
                error="not_found"
            )), 404
        
        return send_file(filepath, mimetype='image/png')
        
    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="Error serving image",
            error=str(e)
        )), 500


@transfer_bp.route('/variations', methods=['POST'])
def generate_variations():
    """Generate variations of an image"""
    try:
        init_models()
        
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify(create_response(
                success=False,
                message="Missing image field",
                error="missing_field"
            )), 400
        
        image_path = Path(data['image'])
        num_variations = int(data.get('num_variations', 4))
        
        variations = gan_inference.generate_variations(str(image_path), num_variations)
        
        # Save variations
        variation_files = []
        for i, var_img in enumerate(variations):
            filename = generate_filename(prefix=f'variation_{i}', extension='png')
            filepath = current_app.config['UPLOAD_FOLDER'] / filename
            var_img.save(filepath)
            variation_files.append(filename)
        
        return jsonify(create_response(
            success=True,
            message="Variations generated successfully",
            data={
                'variations': variation_files
            }
        )), 200
        
    except Exception as e:
        print(f"Error generating variations: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="Error generating variations",
            error=str(e)
        )), 500