# -*- coding: utf-8 -*-
import os
import sys
import logging
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from prometheus_flask_exporter import PrometheusMetrics

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import database and routes (if used)
# from src.models.user import db
# from src.routes.user import user_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Initialize Prometheus Metrics exporter
metrics = PrometheusMetrics(app)

# Register blueprints (if used)
# app.register_blueprint(user_bp, url_prefix='/api')

# Database configuration (uncomment if needed)
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()

# Health check endpoint for OpenShift probes
@app.route('/healthz')
@metrics.do_not_track()
 # Exclude from metrics
def health_check():
    logger.debug("Health check endpoint called")
    # Add more sophisticated checks if needed (e.g., database connection)
    return jsonify(status="OK"), 200

# Static file serving (React/Vue/etc. frontend)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        logger.error("Static folder not configured")
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        logger.info(f"Serving static file: {path}")
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            logger.info("Serving index.html")
            return send_from_directory(static_folder_path, 'index.html')
        else:
            logger.warning("index.html not found")
            # Return a simple default message if index.html is missing
            return jsonify(message="Welcome to the OpenShift Demo App! Configure static/index.html or API routes."), 200

# Example API endpoint (optional)
@app.route('/api/hello')
def hello_api():
    logger.info("API endpoint /api/hello called")
    return jsonify(message="Hello from the API!")

# Error Handling Example (optional)
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 Not Found: {e}")
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 Internal Server Error: {e}", exc_info=True)
    return jsonify(error="Internal Server Error"), 500


if __name__ == '__main__':
    # Run with Gunicorn in production (via Dockerfile CMD), not Flask's dev server
    # Use port 8080 as defined in Dockerfile/OpenShift manifests
    # Debug mode should be False in production
    logger.info("Starting Flask development server (for local testing only)")
    app.run(host='0.0.0.0', port=8080, debug=False)

