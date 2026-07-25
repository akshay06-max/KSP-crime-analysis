"""
Crime Intelligence Query Engine
--------------------------------
Framework-agnostic core logic used by BOTH:
  1. server.py (local Flask server, for testing/demo without a Catalyst account)
  2. handler.py (Catalyst Advanced I/O Function - deploy target)

This separation means the exact same logic that runs locally is what gets
deployed to Catalyst - only the request/response wrapper differs.

Responsibilities:
  - Load the seed dataset (in production this would be Catalyst Data Store / ZCQL)
  - Retrieve relevant records for a natural-language query (simple RAG retrieval)
  - Call the LLM (Anthropic API) to produce a grounded, cited answer
  - Maintain lightweight session context for follow-up questions
  - Provide structured data for the network graph and analytics dashboard
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict, Counter

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "data_seed"

# ---------- Data loading (swap this block for ZCQL queries when deploying to Catalyst) ----------

def _load(name):
    with open(DATA_DIR / f"{name}.json") as f:
        return json.load(f)

FIRS = _load("firs")
ACCUSED = _load("accused")
VICTIMS = _load("victims")
LOCATIONS = _load("locations")
LINKS = _load("links")

ACCUSED_BY_ID = {a["accused_id"]: a for a in ACCUSED}
VICTIM_BY_ID = {v["victim_id"]: v for v in VICTIMS}
LOCATION_BY_ID = {l["location_id"]: l for l in LOCATIONS}

# in-memory session store: {session_id: {"history": [...], "last_filter": {...}}}
SESSIONS = defaultdict(lambda: {"history": [], "last_filter": {}})


# ---------- Retrieval: turn a NL query into a filtered set of FIR records ----------

def _extract_filters(query: str, prior_filter: dict) -> dict:
    """Very lightweight slot extraction. In production, replace with an LLM
    function-call / tool-use step for robust NER (crime type, area, date range,
    accused name, ID). Kept rule-based here so the demo works with zero extra
    API latency for filtering, and falls back to prior_filter for follow-ups."""
    q = query.lower()
    filters = dict(prior_filter)  # inherit context for follow-up queries

    crime_map = {c.lower(): c for c in {f["crime_type"] for f in FIRS}}
    for key, val in crime_map.items():
        if any(word in q for word in key.split()):
            filters["crime_type"] = val

    area_map = {l["area"].lower(): l["area"] for l in LOCATIONS}
    for key, val in area_map.items():
        if key in q:
            filters["area"] = val

    status_map = {s.lower(): s for s in {f["status"] for f in FIRS}}
    for key, val in status_map.items():
        if key in q:
            filters["status"] = val

    m = re.search(r"\b(fir/\d{4}/\d+|acc\d+|vic\d+)\b", q)
    if m:
        filters["direct_id"] = m.group(1).upper()

    if any(w in q for w in ["reset", "new question", "clear filter", "start over"]):
        filters = {}

    return filters


def retrieve(query: str, session_id: str, top_k: int = 8):
    session = SESSIONS[session_id]
    filters = _extract_filters(query, session["last_filter"])
    session["last_filter"] = filters

    results = FIRS
    if filters.get("direct_id"):
        did = filters["direct_id"]
        results = [f for f in FIRS if did in (f["fir_id"].upper(), f["accused_id"], f["victim_id"])]
    else:
        if filters.get("crime_type"):
            results = [f for f in results if f["crime_type"] == filters["crime_type"]]
        if filters.get("area"):
            results = [f for f in results if LOCATION_BY_ID[f["location_id"]]["area"] == filters["area"]]
        if filters.get("status"):
            results = [f for f in results if f["status"] == filters["status"]]

    results = sorted(results, key=lambda f: f["date"], reverse=True)[:top_k]

    enriched = []
    for f in results:
        enriched.append({
            **f,
            "accused": ACCUSED_BY_ID.get(f["accused_id"], {}),
            "victim": VICTIM_BY_ID.get(f["victim_id"], {}),
            "location": LOCATION_BY_ID.get(f["location_id"], {}),
        })
    return enriched, filters


# ---------- LLM call for grounded, cited answers ----------

def build_llm_prompt(query: str, records: list, lang: str) -> dict:
    context_lines = []
    for r in records:
        context_lines.append(
            f"[{r['fir_id']}] {r['date']} | {r['crime_type']} | {r['location']['area']} "
            f"| Accused: {r['accused'].get('name','Unknown')} ({r['accused_id']}, "
            f"prior convictions: {r['accused'].get('prior_convictions','?')}) "
            f"| Victim: {r['victim'].get('name','Unknown')} | Status: {r['status']} "
            f"| MO: {r['modus_operandi']}"
        )
    context = "\n".join(context_lines) if context_lines else "No matching records found."

    lang_instruction = "Respond in Kannada (ಕನ್ನಡ)." if lang == "kn" else "Respond in English."

    system = (
        "You are a Crime Intelligence Assistant for a state police crime database. "
        "Answer ONLY using the FIR records provided in the context below. "
        "Always cite the FIR ID(s) your answer is based on, e.g. (FIR/2024/1003). "
        "If the context does not contain enough information, say so explicitly - "
        "never invent case details, names, or outcomes. Keep answers concise and "
        "written for a police investigator or analyst audience. " + lang_instruction
    )
    user = f"Context (retrieved case records):\n{context}\n\nInvestigator question: {query}"
    return {"system": system, "user": user}


def call_llm(prompt: dict) -> str:
    """Calls the Anthropic API if ANTHROPIC_API_KEY is set; otherwise falls back
    to a deterministic templated answer so the demo works offline / without a key."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _offline_fallback_answer(prompt)

    import urllib.request

    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 600,
        "system": prompt["system"],
        "messages": [{"role": "user", "content": prompt["user"]}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            return "".join(b.get("text", "") for b in data.get("content", []))
    except Exception as e:
        return f"[LLM call failed, showing retrieved records only: {e}]\n" + _offline_fallback_answer(prompt)


def _offline_fallback_answer(prompt: dict) -> str:
    return (
        "(Offline demo mode - no ANTHROPIC_API_KEY set. Showing retrieved records "
        "directly; connect an API key to enable natural-language answers.)\n\n"
        + prompt["user"].split("Investigator question:")[0].replace("Context (retrieved case records):\n", "")
    )


def answer_query(query: str, session_id: str = "default", lang: str = "en"):
    records, filters = retrieve(query, session_id)
    prompt = build_llm_prompt(query, records, lang)
    answer = call_llm(prompt)

    SESSIONS[session_id]["history"].append({"role": "user", "content": query})
    SESSIONS[session_id]["history"].append({"role": "assistant", "content": answer})

    return {
        "answer": answer,
        "sources": [r["fir_id"] for r in records],
        "records": records,
        "filters_applied": filters,
    }


def get_history(session_id: str = "default"):
    return SESSIONS[session_id]["history"]


# ---------- Analytics: network graph + dashboard aggregates ----------

def network_for_accused(accused_id: str = None, min_case_count: int = 2):
    """Builds a node/edge graph. If accused_id given, returns that accused's
    subnetwork; otherwise returns all repeat offenders (appear in >= min_case_count
    FIRs) and their linked victims/locations - i.e. the organized-crime view."""
    counts = Counter(l["accused_id"] for l in LINKS)
    target_ids = [accused_id] if accused_id else [aid for aid, c in counts.items() if c >= min_case_count]

    nodes, edges, seen = [], [], set()
    for aid in target_ids:
        acc = ACCUSED_BY_ID.get(aid)
        if not acc or aid in seen:
            continue
        seen.add(aid)
        nodes.append({"id": aid, "label": acc["name"], "type": "accused",
                       "cases": counts[aid]})
        for l in LINKS:
            if l["accused_id"] != aid:
                continue
            vid, lid, fid = l["victim_id"], l["location_id"], l["fir_id"]
            if vid not in seen:
                v = VICTIM_BY_ID[vid]
                nodes.append({"id": vid, "label": v["name"], "type": "victim"})
                seen.add(vid)
            if lid not in seen:
                loc = LOCATION_BY_ID[lid]
                nodes.append({"id": lid, "label": loc["area"], "type": "location"})
                seen.add(lid)
            edges.append({"from": aid, "to": vid, "label": fid})
            edges.append({"from": aid, "to": lid, "label": "incident at"})

    return {"nodes": nodes, "edges": edges}


def dashboard_stats():
    crime_counts = Counter(f["crime_type"] for f in FIRS)
    area_counts = Counter(LOCATION_BY_ID[f["location_id"]]["area"] for f in FIRS)
    status_counts = Counter(f["status"] for f in FIRS)
    month_counts = Counter(f["date"][:7] for f in FIRS)

    repeat_offender_ids = [aid for aid, c in Counter(l["accused_id"] for l in LINKS).items() if c >= 2]

    return {
        "total_firs": len(FIRS),
        "crime_type_breakdown": dict(crime_counts.most_common()),
        "area_breakdown": dict(area_counts.most_common()),
        "status_breakdown": dict(status_counts),
        "monthly_trend": dict(sorted(month_counts.items())),
        "repeat_offender_count": len(repeat_offender_ids),
        "top_hotspot": area_counts.most_common(1)[0] if area_counts else None,
    }


def risk_score(accused_id: str):
    """Simple, transparent (explainable) risk scorecard - NOT a black box.
    Score components and weights are shown to the user in the response."""
    acc = ACCUSED_BY_ID.get(accused_id)
    if not acc:
        return None
    case_count = sum(1 for l in LINKS if l["accused_id"] == accused_id)
    prior = acc.get("prior_convictions", 0)
    crime_types = {f["crime_type"] for f in FIRS if f["accused_id"] == accused_id}

    components = {
        "prior_convictions_score": min(prior * 15, 45),
        "case_frequency_score": min(case_count * 10, 30),
        "crime_diversity_score": min(len(crime_types) * 5, 15),
        "recency_score": 10 if any(f["date"] > "2026-01-01" for f in FIRS if f["accused_id"] == accused_id) else 0,
    }
    total = sum(components.values())
    band = "High" if total >= 60 else "Medium" if total >= 30 else "Low"

    return {
        "accused_id": accused_id, "name": acc["name"], "total_score": total,
        "band": band, "components": components, "linked_case_count": case_count,
        "explanation": (
            f"Score = prior convictions ({components['prior_convictions_score']}/45) + "
            f"case frequency ({components['case_frequency_score']}/30) + "
            f"crime-type diversity ({components['crime_diversity_score']}/15) + "
            f"recent activity ({components['recency_score']}/10)."
        ),
    }
