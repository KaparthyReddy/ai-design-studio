from flask import Blueprint, request, jsonify, current_app
from pathlib import Path
import json
from datetime import datetime

from utils.model_utils import create_response, cleanup_old_files
from utils.image_processing import ImageProcessor

gallery_bp = Blueprint('gallery', __name__)

# Simple in-memory gallery storage (in production, use a database)
gallery_storage = []


@gallery_bp.route('/gallery', methods=['GET'])
def get_gallery():
    """Get all saved images in gallery"""
    try:
        # Get all images from uploads folder
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        images = []
        for file_path in upload_folder.glob('styled_*.png'):
            try:
                img_info = ImageProcessor.get_image_info(file_path)
                images.append({
                    'filename': file_path.name,
                    'created_at': datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat(),
                    'info': img_info
                })
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                continue
        
        # Sort by creation time (newest first)
        images.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify(create_response(
            success=True,
            message="Gallery retrieved successfully",
            data={
                'images': images,
                'count': len(images)
            }
        )), 200
        
    except Exception as e:
        print(f"Error retrieving gallery: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="Error retrieving gallery",
            error=str(e)
        )), 500


@gallery_bp.route('/gallery/<filename>', methods=['DELETE'])
def delete_from_gallery(filename):
    """Delete an image from gallery"""
    try:
        filepath = current_app.config['UPLOAD_FOLDER'] / filename
        
        if not filepath.exists():
            return jsonify(create_response(
                success=False,
                message="Image not found",
                error="not_found"
            )), 404
        
        filepath.unlink()
        
        return jsonify(create_response(
            success=True,
            message="Image deleted successfully",
            data={'filename': filename}
        )), 200
        
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="Error deleting image",
            error=str(e)
        )), 500


@gallery_bp.route('/gallery/cleanup', methods=['POST'])
def cleanup_gallery():
    """Clean up old images from gallery"""
    try:
        data = request.get_json() or {}
        max_age_hours = int(data.get('max_age_hours', 24))
        
        deleted_count = cleanup_old_files(
            current_app.config['UPLOAD_FOLDER'],
            max_age_hours=max_age_hours
        )
        
        return jsonify(create_response(
            success=True,
            message=f"Cleanup completed. {deleted_count} files deleted",
            data={'deleted_count': deleted_count}
        )), 200
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="Error during cleanup",
            error=str(e)
        )), 500


@gallery_bp.route('/gallery/info', methods=['GET'])
def gallery_info():
    """Get gallery statistics"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        total_files = len(list(upload_folder.glob('*.png'))) + \
                     len(list(upload_folder.glob('*.jpg'))) + \
                     len(list(upload_folder.glob('*.jpeg')))
        
        styled_files = len(list(upload_folder.glob('styled_*.png')))
        
        # Calculate total size
        total_size = sum(
            f.stat().st_size 
            for f in upload_folder.iterdir() 
            if f.is_file() and f.name != '.gitkeep'
        )
        total_size_mb = total_size / (1024 * 1024)
        
        return jsonify(create_response(
            success=True,
            message="Gallery info retrieved",
            data={
                'total_files': total_files,
                'styled_files': styled_files,
                'total_size_mb': round(total_size_mb, 2),
                'upload_folder': str(upload_folder)
            }
        )), 200
        
    except Exception as e:
        print(f"Error getting gallery info: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="Error getting gallery info",
            error=str(e)
        )), 500
