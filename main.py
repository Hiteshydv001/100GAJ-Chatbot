# main.py (Final Version - Fast Startup)

import logging
import atexit
from flask import Flask, jsonify
from flask_cors import CORS

from app.api.v1.endpoints.chat_flask import chat_bp
from app.core.async_worker import async_worker

# Create the Flask application instance
app = Flask(__name__)

# Apply CORS to allow cross-origin requests from any source
CORS(app)

# Configure basic logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Register the API routes from our chat_flask.py file
app.register_blueprint(chat_bp, url_prefix='/api/v1')

# The root URL (/) serves as a simple, fast health check.
@app.route("/", methods=["GET"])
def health_check():
    """A simple health check endpoint to confirm the server is running."""
    return jsonify({
        "status": "ok",
        "message": "100Gaj API is running. Use /api/v1/chat to interact."
    })

# The AI engine will now be loaded on-demand by the first API request.
# Because it uses the pre-built cache from your repository, this will be fast.
# Startup of this server process is now instant.

# Gracefully stop the background worker thread when the app exits
atexit.register(lambda: async_worker.stop())

# This block is only for running the app locally for development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)