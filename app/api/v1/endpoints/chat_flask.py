# app/api/v1/endpoints/chat_flask.py

import json
import logging
from flask import Blueprint, request, Response
from typing import List, AsyncGenerator

# --- THE CRITICAL FIX ---
# Import the global chat_engine instance from your main app file.
# This object is already initialized and ready to use.
from main import chat_engine

from llama_index.core.llms import ChatMessage, MessageRole
from app.core.async_worker import async_worker

chat_bp = Blueprint('chat_api', __name__)
logger = logging.getLogger(__name__)

async def process_chat_stream(user_message: str, history: List[dict]) -> AsyncGenerator[str, None]:
    """
    The core async logic that runs in the background thread's event loop.
    """
    # Use the pre-loaded engine. This part is now extremely fast.
    agent = chat_engine 

    if agent is None:
        logger.error("Chat engine is not available.")
        error_msg = json.dumps({"type": "text", "data": "I'm sorry, the chat service is not initialized correctly. Please try again later."})
        yield f"data: {error_msg}\n\n"
        return

    chat_history: List[ChatMessage] = []
    for msg in history:
        role = MessageRole.USER if msg.get("role") == 'user' else MessageRole.ASSISTANT
        chat_history.append(ChatMessage(role=role, content=msg.get("content", "")))

    try:
        response = await agent.achat(user_message, chat_history=chat_history)

        if not response or not hasattr(response, 'response'):
            error_msg = json.dumps({"type": "text", "data": "I apologize, but I've encountered an error and could not get a response."})
            yield f"data: {error_msg}\n\n"
            return

        message = json.dumps({"type": "text", "data": response.response})
        yield f"data: {message}\n\n"
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    except Exception as e:
        logger.error(f"Unexpected error in chat stream: {str(e)}", exc_info=True)
        error_msg = json.dumps({"type": "text", "data": "I'm sorry, an unexpected error occurred while processing your request."})
        yield f"data: {error_msg}\n\n"

@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    The main Flask route. It delegates the async processing to the worker.
    """
    data = request.get_json()
    if not data or "message" not in data:
        return Response(json.dumps({"error": "Message not provided"}), status=400, mimetype='application/json')

    user_message = data["message"]
    history = data.get("history", [])

    def generate():
        """
        A sync generator that gets results from the async worker's generator.
        """
        async_gen = process_chat_stream(user_message, history)
        yield from async_worker.run_async_generator(async_gen)

    return Response(generate(), mimetype='text/event-stream')