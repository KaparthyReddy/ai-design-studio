import os
from pathlib import Path

class Config:
    """Base configuration"""
    
    # Base directory
    BASE_DIR = Path(__file__).parent
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Upload settings
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Model settings
    PRETRAINED_MODELS_PATH = BASE_DIR / 'pretrained_models'
    MODEL_DEVICE = 'mps'  # For Apple Silicon M4
    
    # Image processing settings
    IMAGE_SIZE = 512
    STYLE_WEIGHT = 1000000
    CONTENT_WEIGHT = 1
    NUM_STEPS = 300
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Create necessary directories
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.PRETRAINED_MODELS_PATH.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}