import hmac
import os
import threading

from flask import Flask, jsonify, request
from interpreter import interpreter

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

MODEL = os.getenv("INTERPRETER_MODEL", "gemini/gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CHAT_API_TOKEN = os.getenv("CHAT_API_TOKEN", "")
AUTO_RUN = os.getenv("INTERPRETER_AUTO_RUN", "false").strip().lower() == "true"

interpreter.llm.model = MODEL
if GEMINI_API_KEY:
    interpreter.llm.api_key = GEMINI_API_KEY
interpreter.auto_run = AUTO_RUN

# The interpreter is stateful; serialize requests to avoid concurrent corruption.
_chat_lock = threading.Lock()


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.post("/chat")
def chat():
    if not CHAT_API_TOKEN or not GEMINI_API_KEY:
        return jsonify({"error": "Chat service is not configured"}), 503

    auth = request.headers.get("Authorization", "")
    supplied_token = auth[7:] if auth.startswith("Bearer ") else ""
    if not hmac.compare_digest(supplied_token, CHAT_API_TOKEN):
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True)
    message = payload.get("message") if isinstance(payload, dict) else None
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "JSON field 'message' must be a non-empty string"}), 400
    if len(message) > 8000:
        return jsonify({"error": "Message exceeds 8000 characters"}), 413

    try:
        with _chat_lock:
            response = interpreter.chat(message.strip())
        return jsonify({"response": response})
    except Exception:
        app.logger.exception("Interpreter chat request failed")
        return jsonify({"error": "Interpreter request failed"}), 502


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({"error": "Request body exceeds 64 KiB"}), 413


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
        use_reloader=False,
    )
