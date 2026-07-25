"""
Catalyst Advanced I/O Function: chatQuery
-------------------------------------------
Deploy this folder as a Catalyst Python "Advanced I/O Function".
Endpoints (all via a single function, routed by `action` in the JSON body):

  POST /server/chatQuery
  {
    "action": "chat" | "network" | "dashboard" | "risk_score" | "history",
    "query": "...",          # for action=chat
    "session_id": "...",     # optional, defaults to "default"
    "lang": "en" | "kn",     # optional, defaults to "en"
    "accused_id": "..."      # for action=network / risk_score
  }

Catalyst deployment notes:
  - Set ANTHROPIC_API_KEY as a Catalyst environment variable
    (Console > Functions > chatQuery > Environment Variables)
  - This function has no external Catalyst SDK dependency for the demo
    (uses local JSON as the data source). For production, replace
    engine.py's `_load()` calls with ZCQL queries against Catalyst Data
    Store tables (FIRS, ACCUSED, VICTIMS, LOCATIONS) - see README.
"""

import json
import engine


def handler(request, response):
    """Catalyst Advanced I/O function signature: (request, response)."""
    try:
        body = json.loads(request.getBody() or "{}")
    except Exception:
        body = {}

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

    response.setContentType("application/json")
    response.setStatus(200)
    response.setBody(json.dumps(result))
    response.send()


# Catalyst looks for a function named exactly like the entry point configured
# in catalyst-config.json (see ../catalyst-config.json -> "handler": "handler.handler")
