# Climate Disinformation Lab

An interactive workbench for technique-based inoculation against climate disinformation.

Given a factual climate statement or an extreme-weather headline, the Lab generates one
labelled distortion for each of five rhetorical clusters, expands sub-techniques on demand,
and shows every variant beside the original fact. Each cluster is paired with a
fact–myth–fallacy counter-message.

> The tool generates deceptive content by design. Its purpose is inoculation: showing the
> same fact bent by one labelled technique after another so the techniques become
> recognisable. Generated text is for research and education only.

---

## Taxonomy: 5 Clusters

The taxonomy synthesizes FLICC (reasoning errors), CARDS (contrarian claims) and the
discourses-of-delay typology. Every technique is a modular prompt template, so each
generated variant carries its technique label.

| Cluster | Core mechanism | Sub-techniques (examples) |
|---------|----------------|---------------------------|
| **Denial** | Reject factual claims | fake experts, trend skepticism, attribution skepticism |
| **Doubt-Casting** | Undermine confidence in the science | cherry picking, impossible expectations, model attacks |
| **Deflection** | Shift responsibility | other countries, whataboutism, individual responsibility transfer |
| **Delay** | Oppose action now | tech salvation, economic cost, moving goalposts |
| **Conspiracy** | Attribute findings to malicious actors | nefarious intent, global conspiracy, cover-up |

The full definition lives in `data/unified_taxonomy.json`.

---

## Features

- **Transformation graph** — a root statement connected to five cluster variants (ReactFlow).
- **Sub-technique expansion** — each cluster node offers further techniques, generated on click.
- **Personas and formats** — drag persona chips (country, generation, politics) or a
  publication format onto a node to re-target the variant.
- **News mode** — start from scraped extreme-weather headlines (`data/news_headlines.json`).
- **Model selector** — choose the generator model.
- **Counter-messaging** — technique-level warning plus fact–myth–fallacy correction per cluster.

---

## Architecture

```
React frontend (ReactFlow graph)
    ↓ HTTP REST
Flask backend
    ├── DisinformationInjector    ← layered prompt assembly (cluster + technique + persona + format)
    ├── DisinformationDetector    ← rule-based 5-cluster detection
    ├── CounterMessagingModule    ← prebunking templates
    └── BedrockLLMService         ← AWS Bedrock via an HTTP proxy
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Access to an AWS Bedrock proxy endpoint (ID + API token)

### 1. Backend
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-core.txt

cp .env.example .env.bedrock
# Edit .env.bedrock: BEDROCK_TEAM_ID, BEDROCK_API_TOKEN, BEDROCK_API_ENDPOINT

cd backend && python api.py
# → http://localhost:5000
```

### 2. Frontend
```bash
cd frontend-react
npm install
npm start
# → http://localhost:3000
```

### 3. Verify
```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/taxonomy/clusters
```

### 4. Refresh headlines (optional)
```bash
python scripts/fetch_news.py
```

---

## API Endpoints

```
GET  /api/health                        Health check
GET  /api/taxonomy/clusters             All 5 clusters with techniques
GET  /api/taxonomy/clusters/<id>        Single cluster detail
GET  /api/personas                      Persona attributes
GET  /api/content-formats               Publication formats
GET  /api/models                        Available generator models
GET  /api/news/headlines                Headlines (search, filter, pagination)
POST /api/graph/expand                  Statement → 5 cluster variants
POST /api/transform                     Persona / format / sub-technique variant
POST /api/graph/evaluate                Detect disinformation techniques in text
GET  /api/counter/prebunking/<cluster>  Prebunking message
```

---

## Deployment (Cloud Run)

```bash
gcloud builds submit --config cloudbuild.bedrock.yaml
```

Bedrock credentials are supplied through Secret Manager; see the comment in
`cloudbuild.bedrock.yaml`. `setup_scheduler.sh` provisions the scheduled headline scraper.

---

## Status

The workbench has not undergone user evaluation. No claims are made about persuasive
efficacy or inoculation effect.
