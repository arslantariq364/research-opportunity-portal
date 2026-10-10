"""
Application factory and entry point for University Research Opportunity Portal.
Phase 2/3: Complete REST API and Academic SaaS Frontend Delivery.
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
    frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path='/static'
    )
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register API blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/', methods=['GET'])
    def root():
        """Root API status endpoint."""
        return jsonify({
            "project": "University Research Opportunity Portal",
            "phase": "Academic Research Dashboard (Phase 3)",
            "status": "ready",
            "portal_url": "/portal"
        }), 200

    @app.route('/portal', methods=['GET'])
    def portal():
        """Serve the academic research dashboard frontend interface."""
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/css/<path:filename>', methods=['GET'])
    def serve_css(filename):
        """Serve CSS assets."""
        return send_from_directory(os.path.join(frontend_dir, 'css'), filename)

    @app.route('/js/<path:filename>', methods=['GET'])
    def serve_js(filename):
        """Serve JavaScript assets."""
        return send_from_directory(os.path.join(frontend_dir, 'js'), filename)

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
