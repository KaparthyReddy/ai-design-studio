from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import os
from dotenv import load_dotenv

from config import config
from routes import register_routes

# Load environment variables
load_dotenv()

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS']
        }
    })
    
    # Register routes
    register_routes(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'AI Design Studio API is running',
            'device': app.config['MODEL_DEVICE']
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║   AI Design Studio - Backend Server     ║
    ╚══════════════════════════════════════════╝
    
    🚀 Server starting...
    📍 URL: http://{app.config['HOST']}:{app.config['PORT']}
    🎨 Device: {app.config['MODEL_DEVICE']}
    🔧 Environment: {os.getenv('FLASK_ENV', 'development')}
    
    Press CTRL+C to stop
    """)
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
