# Prototype Brief — Setu: Intelligent Conversational AI for KSP Crime Database

## Problem Statement Addressed
State crime databases are rich but hard to query — investigators and
analysts need SQL/technical skill to retrieve FIR, accused, victim, or
case-status information, and hidden patterns (repeat-offender networks,
hotspots, risk indicators) go undiscovered without dedicated analytics
effort. Setu addresses this with a natural-language conversational layer
over crime records, combined with network analysis, trend analytics, and
explainable offender risk scoring — moving beyond simple data retrieval
toward investigative decision support.

## Key Features & Functionalities
1. **Conversational Crime Intelligence Interface** — natural-language chat
   in English and Kannada; retrieves FIR, accused, victim, location, and
   case-status information; context-aware follow-up queries within a
   session; every answer cites the FIR ID(s) it is grounded on.
2. **Conversation export to PDF** — one-click, saved locally, for case
   documentation.
3. **Criminal Network & Relationship Analysis** — interactive graph of
   repeat offenders and their linked victims/locations, surfacing
   organized/recurring-crime patterns that aren't visible in a flat table.
4. **Crime Pattern & Trend Analytics dashboard** — crime-type mix,
   geographic hotspots, monthly trend, and case-status breakdown.
5. **Criminology-based offender risk scoring** — a transparent, explainable
   scorecard (prior convictions, case frequency, crime-type diversity,
   recency of activity) to help prioritize investigative attention, with
   every score's components shown — not a black-box output.

## Technology Stack
- **Backend**: Python 3.12, deployed as a Zoho Catalyst Advanced I/O
  Function (`chatQuery`)
- **Data layer**: JSON seed dataset for the demo, designed to map directly
  onto Catalyst Data Store (ZCQL) tables for production use
- **LLM**: Anthropic Claude API for grounded, citation-required
  natural-language answers (with an offline fallback mode so the app is
  fully demoable without external dependency)
- **Frontend**: Vanilla HTML/CSS/JS on Catalyst Web Hosting; vis-network
  (graph visualization), Chart.js (analytics charts), jsPDF (export)
- **Deployment**: Zoho Catalyst (per hackathon requirement)

## Proposed Impact & Use Case
- **Investigators**: get FIR/accused/victim/status information conversationally,
  in their own language, without writing queries — faster case lookups
  during active investigation.
- **Analysts**: surface repeat-offender networks and hotspot patterns that
  are otherwise buried across hundreds of individual FIRs, supporting
  proactive patrol deployment and organized-crime detection.
- **Supervisors/Policymakers**: dashboard-level trend visibility (crime mix,
  geographic distribution, case pipeline status) to inform resourcing
  decisions.
- **Explainability by design**: every AI-generated answer and every risk
  score is traceable to source records or transparent scoring logic,
  supporting the accountability requirements of law-enforcement use of AI.

## Roadmap beyond this prototype
Voice interaction, financial transaction / money-trail linking, predictive
crime forecasting, full role-based access control with audit logging, and
socio-economic correlation analysis (requires integration with external
census/ward-level data) are part of the full solution vision but are
out of scope for this 6-day prototype. See `README.md` §2 for the
complete status table.
