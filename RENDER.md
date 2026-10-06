# Render deployment

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Set `GEMINI_API_KEY` and a long, random `CHAT_API_TOKEN` in Render's Environment settings.
- Send chat requests with `Authorization: Bearer <CHAT_API_TOKEN>` and JSON `{"message":"..."}`.
- `INTERPRETER_AUTO_RUN` defaults to `false`. Only set it to `true` for a sandboxed deployment: the interpreter can execute generated code on the service host.
- `/healthz` is the health-check path.

The existing `python app.run` start command remains supported; Gunicorn is recommended for production.
