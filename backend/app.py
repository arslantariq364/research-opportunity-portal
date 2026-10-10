"""
Application factory and entry point for University Research Opportunity Portal.
Phase 1: Project Scaffolding and Database Connectivity.
"""
import os
import sys

# Ensure backend directory and project root are discoverable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

for path in (PROJECT_ROOT, CURRENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from backend.config import Config
    from backend.models import db
    from backend.routes import api_bp
except ImportError:
    from config import Config
    from models import db
    from routes import api_bp


def create_app(config_class=Config):
    """Factory function to initialize and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/', methods=['GET'])
    def root():
        """Root API status endpoint for Phase 1 verification."""
        return jsonify({
            "project": "University Research Opportunity Portal",
            "phase": "Phase 1: Project Structure & Database Design",
            "status": "ready"
        }), 200

    return app

if __name__ == '__main__':
    from flask import Flask, jsonify
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    from flask import Flask, jsonify
