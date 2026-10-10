"""
Application factory and entry point for University Research Opportunity Portal.
Phase 2: Complete REST API Implementation.
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

from flask import Flask, jsonify, send_from_directory


def create_app(config_class=Config):
    """Factory function to initialize and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register API blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/', methods=['GET'])
    def root():
        """Root API status endpoint for Phase 2 verification."""
        return jsonify({
            "project": "University Research Opportunity Portal",
            "phase": "Phase 2: Complete REST API Implementation",
            "status": "ready"
        }), 200

    @app.route('/portal', methods=['GET'])
    def portal():
        """Serve frontend scaffolding interface."""
        return send_from_directory(os.path.join(PROJECT_ROOT, 'frontend'), 'index.html')

    @app.route('/frontend/<path:filename>', methods=['GET'])
    def frontend_assets(filename):
        """Serve frontend static assets (CSS, JS)."""
        return send_from_directory(os.path.join(PROJECT_ROOT, 'frontend'), filename)

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
