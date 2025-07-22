# main.py (API-Only Version for Production)

import logging
import atexit
from flask import Flask, jsonify
from flask_cors import CORS

from app.api.v1.endpoints.chat_flask import chat_bp
from app.core.engine import get_chat_engine
from app.core.tools.api_property_search import _fetch_all_data
from app.core.async_worker import async_worker

app = Flask(__name__)
CORS(app) # Allows requests from any origin, which is needed for Postman/local files.

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Register the API routes
app.register_blueprint(chat_bp, url_prefix='/api/v1')

# The root URL (/) now serves as the health check.
@app.route("/", methods=["GET"])
def health_check():
    """A simple health check endpoint to confirm the server is running."""
    return jsonify({
        "status": "ok",
        "message": "100Gaj API is running. Use /api/v1/chat to interact."
    })

# Logic to pre-load models and data on server startup
with app.app_context():
    logging.info("Application starting up...")
    get_chat_engine()
    _fetch_all_data()
    logging.info("Startup complete. Models and data are loaded.")

atexit.register(lambda: async_worker.stop())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)