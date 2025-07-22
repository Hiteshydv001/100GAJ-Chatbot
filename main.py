# main.py

import logging
import atexit
from flask import Flask, jsonify
from flask_cors import CORS

from app.api.v1.endpoints.chat_flask import chat_bp
from app.core.engine import get_chat_engine
from app.core.tools.api_property_search import _fetch_all_data
from app.core.async_worker import async_worker

# Create the Flask application instance
app = Flask(__name__)

# Apply CORS to allow cross-origin requests
CORS(app)

# Configure basic logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Register the API routes from our chat_flask.py file
app.register_blueprint(chat_bp, url_prefix='/api/v1')

# The root URL (/) now serves as the health check.
@app.route("/", methods=["GET"])
def health_check():
    """A simple health check endpoint to confirm the server is running."""
    return jsonify({
        "status": "ok",
        "message": "100Gaj API is running. Use /api/v1/chat to interact."
    })

# Logic to pre-load the engine and data ONCE when the application starts.
with app.app_context():
    logging.info("Application starting up... Loading AI engine.")
    
    # Load the engine and attach it directly to the Flask app object.
    # This makes it accessible via `current_app.chat_engine` elsewhere.
    app.chat_engine = get_chat_engine()
    
    # Pre-fetch property data
    _fetch_all_data()
    
    logging.info("Startup complete. AI Engine and data are loaded and ready.")

# Gracefully stop the background worker thread when the app exits
atexit.register(lambda: async_worker.stop())

# This block is only for running the app locally (e.g., `python main.py`)
# It is NOT used by Gunicorn in production.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)