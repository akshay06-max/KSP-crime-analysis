"""
Local test server - mirrors handler.py's routing but runs on Flask so you can
develop and demo entirely on your laptop before deploying to Catalyst.

Run:
    pip install -r ../../requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...   # optional - works offline without it
    python3 server.py
Then open client/index.html in a browser (it points at http://localhost:5000).
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import engine

app = Flask(__name__)
CORS(app)  # allow the static client/index.html (opened via file:// or a simple server) to call this API


@app.route("/server/chatQuery", methods=["POST"])
def chat_query():
    body = request.get_json(force=True) or {}
    action = body.get("action", "chat")
    session_id = body.get("session_id", "default")
    lang = body.get("lang", "en")

    if action == "chat":
        result = engine.answer_query(body.get("query", ""), session_id, lang)
    elif action == "network":
        result = engine.network_for_accused(body.get("accused_id"))
    elif action == "dashboard":
        result = engine.dashboard_stats()
    elif action == "risk_score":
        result = engine.risk_score(body.get("accused_id", ""))
    elif action == "history":
        result = {"history": engine.get_history(session_id)}
    else:
        result = {"error": f"Unknown action: {action}"}

    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("Crime Intelligence API running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
