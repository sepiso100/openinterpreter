# Render deployment

This repository's web app is the Python Flask application in `app.py`. Create a **Python web service** for this repository (or use a Docker service configured with Python); do not run it as a Node service. The repository pins Python 3.12.11 in `.python-version`.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Health-check path: `/healthz`
- Set `GEMINI_API_KEY` and a long, random `CHAT_API_TOKEN` in Render's Environment settings.
- Send chat requests with `Authorization: Bearer <CHAT_API_TOKEN>` and JSON `{"message":"..."}`.
- `INTERPRETER_AUTO_RUN` defaults to `false`. Only set it to `true` for a sandboxed deployment: the interpreter can execute generated code on the service host.

The existing `python app.run` development command is not a production start command. Use Gunicorn for the Render web service.
