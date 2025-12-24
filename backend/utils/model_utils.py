import os
import time
from pathlib import Path
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime, timedelta

def allowed_file(filename, allowed_extensions):
    """
    Check if file extension is allowed
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
    
    Returns:
        Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_filename(prefix='image', extension='png'):
    """
    Generate unique filename with timestamp
    
    Args:
        prefix: Prefix for filename
        extension: File extension
    
    Returns:
        Unique filename string
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{random_str}.{extension}"


def cleanup_old_files(directory, max_age_hours=24):
    """
    Clean up old files from directory
    
    Args:
        directory: Path to directory
        max_age_hours: Maximum age of files in hours
    
    Returns:
        Number of files deleted
    """
    directory = Path(directory)
    if not directory.exists():
        return 0
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    deleted_count = 0
    
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.name != '.gitkeep':
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if file_time < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    return deleted_count


def get_file_size_mb(file_path):
    """Get file size in megabytes"""
    return Path(file_path).stat().st_size / (1024 * 1024)


def validate_image_size(file_path, max_size_mb=16):
    """
    Validate image file size
    
    Args:
        file_path: Path to image file
        max_size_mb: Maximum allowed size in MB
    
    Returns:
        Tuple (is_valid, size_mb)
    """
    size_mb = get_file_size_mb(file_path)
    return size_mb <= max_size_mb, size_mb


def create_response(success, message, data=None, error=None):
    """
    Create standardized API response
    
    Args:
        success: Boolean indicating success
        message: Response message
        data: Optional data payload
        error: Optional error details
    
    Returns:
        Dictionary response
    """
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if error is not None:
        response['error'] = error
    
    return response


def sanitize_filename(filename):
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Use werkzeug's secure_filename
    filename = secure_filename(filename)
    
    # Additional sanitization
    filename = filename.replace(' ', '_')
    filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
    
    return filename


def get_model_info(device):
    """
    Get information about the current model/device setup
    
    Returns:
        Dictionary with model information
    """
    import torch
    
    info = {
        'device': str(device),
        'pytorch_version': torch.__version__,
        'mps_available': torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False,
        'cuda_available': torch.cuda.is_available(),
    }
    
    return info


def format_time(seconds):
    """Format seconds into readable time string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"