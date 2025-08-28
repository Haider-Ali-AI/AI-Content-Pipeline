from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from .models import db, DraftArticle
from .routes.dashboard import dashboard_bp
from .routes.approve import approve_bp
from .config import Config
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    # Serve static assets from the frontend's build folder
    app = Flask(__name__, static_folder='../frontend/dist/assets', static_url_path='/assets')
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'])
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(approve_bp, url_prefix='/api')
    
    # Serve the React App from the dist folder
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join('../frontend/dist', path)):
            return send_from_directory('../frontend/dist', path)
        else:
            return send_from_directory('../frontend/dist', 'index.html')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'AI News Automation API is running',
            'gemini_configured': bool(Config.GEMINI_API_KEY)
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create tables
    with app.app_context():
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Create database tables
        db.create_all()
        
        logger.info("Database tables created successfully")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)