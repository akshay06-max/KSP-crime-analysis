# Demo Video Script (target: 4 minutes)

Record your screen (OBS Studio / Loom / Windows Game Bar) with voiceover.
Upload unlisted to YouTube or a public Google Drive link, then test the
link yourself in an incognito window before submitting.

---

**0:00–0:30 — Problem statement**
"State crime databases hold thousands of FIRs but are hard to query
without SQL knowledge, and patterns like repeat-offender networks stay
hidden in flat tables. We built Setu — a conversational AI and analytics
layer over the crime database."
*(Show a title slide or the PROTOTYPE_BRIEF.md on screen.)*

**0:30–1:30 — Conversational query (core feature)**
- Open the deployed app, land on "Conversational Query" tab.
- Type: "Show me chain snatching cases in Indiranagar" → show the answer
  with cited FIR ID.
- Ask a natural follow-up: "What about the accused's prior record?" →
  show context is retained without repeating filters.
- Switch language dropdown to ಕನ್ನಡ, ask a question in Kannada → show
  Kannada response.
- Click "Export conversation (PDF)" → show the downloaded PDF opening.

**1:30–2:30 — Network analysis**
- Go to "Network Analysis" tab → click "Load repeat-offender network."
- Point out: node size = number of linked cases, hover to show connections
  to victims/locations, explain this surfaces organized/recurring crime
  patterns invisible in a flat FIR list.
- Type a specific accused ID into the subnetwork filter to show drill-down.

**2:30–3:15 — Pattern & trend dashboard**
- Go to "Pattern & Trends" tab.
- Walk through: crime-type breakdown, hotspot area chart, monthly trend
  line, case-status pipeline (how many under investigation vs. closed).

**3:15–3:45 — Offender risk scoring (explainable AI)**
- Go to "Offender Risk Scoring" tab → click "Load top offenders."
- Point out the score breakdown is fully visible (prior convictions, case
  frequency, diversity, recency) — "this is a transparent scorecard, not
  a black box, so every recommendation is auditable."

**3:45–4:00 — Close**
"This is deployed on Zoho Catalyst, with source code and setup docs on
GitHub. Roadmap items — financial link analysis, forecasting, and voice
— are outlined in our README as next steps."
