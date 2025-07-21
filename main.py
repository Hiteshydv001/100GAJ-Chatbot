# main.py (Final Corrected Version)

import logging
import atexit
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from app.api.v1.endpoints.chat_flask import chat_bp
from app.core.engine import get_chat_engine
from app.core.tools.api_property_search import _fetch_all_data
from app.core.async_worker import async_worker

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app.register_blueprint(chat_bp, url_prefix='/api/v1')

# --- This is the route that was missing on your server ---
@app.route("/")
def serve_index():
    """Serves the main chat interface (index.html)."""
    return send_from_directory('.', 'index.html')

# A dedicated health check for Render.
@app.route("/health")
def health_check():
    """A simple health check endpoint to confirm the server is running."""
    return jsonify({"status": "ok"})

# Logic to pre-load models and data on server startup
with app.app_context():
    logging.info("Application starting up...")
    get_chat_engine()
    _fetch_all_data()
    logging.info("Startup complete. Models and data are loaded.")

atexit.register(lambda: async_worker.stop())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)