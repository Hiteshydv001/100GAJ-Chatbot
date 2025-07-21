# main.py (Corrected for Production)

import logging
import atexit
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from app.api.v1.endpoints.chat_flask import chat_bp
from app.core.async_worker import async_worker

# --- This is the key change ---
# We no longer import get_chat_engine or _fetch_all_data for startup

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app.register_blueprint(chat_bp, url_prefix='/api/v1')

# --- This part is now correct ---
# The root route serves your user interface.
@app.route("/")
def serve_index():
    return send_from_directory('.', 'index.html')

# A dedicated health check for Render.
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "100Gaj Flask API is running"
    })

# --- The slow startup logic has been REMOVED ---
# This makes the server start instantly.
# The AI engine will load on the first API request, using the pre-built cache.

atexit.register(lambda: async_worker.stop())

# This part is for local testing but is not used by Gunicorn on Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)