"""
Routes package for AI Design Studio API
"""

from flask import Blueprint
from .transfer import transfer_bp
from .gallery import gallery_bp

def register_routes(app):
    """Register all blueprints with the Flask app"""
    
    # Register blueprints
    app.register_blueprint(transfer_bp, url_prefix='/api')
    app.register_blueprint(gallery_bp, url_prefix='/api')
    
    print("✅ All routes registered successfully")

__all__ = ['register_routes', 'transfer_bp', 'gallery_bp']