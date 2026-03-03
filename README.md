# Climate Disinformation Lab

**UCL Workspaces — LLM Susceptibility Testing for Climate Disinformation**

An interactive research tool that tests how large language models amplify climate disinformation
under multi-turn conversational priming, using a unified 5-cluster taxonomy merging FLICC,
CARDS v2, and the 4D Framework.

---

## Research Question

> How susceptible are LLMs to climate disinformation amplification when subjected to
> multi-turn conversational priming — and does susceptibility vary systematically by
> disinformation cluster?

---

## Architecture

Same pattern as `art-of-biasing-LLM`, adapted for climate disinformation:

| Component | Bias Workspace | This Workspace |
|-----------|---------------|----------------|
| Domain | Cognitive bias injection | Climate disinformation priming |
| Dataset | EMGSD (1,158 stereotype entries) | Climate questions × 5 clusters |
| Framework | BEATS / Sun & Kok / HEARTS | FLICC / CARDS / 4D |
| Taxonomy | 8 cognitive bias types | 5 disinformation clusters |
| Counter-measure | Debiasing | Prebunking / Debunking |
| Backend | Flask + Bedrock | Flask + Bedrock |
| Frontend | React + ReactFlow | React + ReactFlow |

```
React Frontend (ReactFlow Graph)
    ↓ HTTP REST
Flask Backend (port 5000)
    ├── DisinformationDetector    ← Rule-based 5-cluster detection
    ├── DisinformationInjector    ← Multi-turn priming generation
    ├── CounterMessagingModule    ← Prebunking + Debunking
    └── BedrockLLMService         ← AWS Bedrock Proxy (Nova Pro / Claude)
```

---

## Taxonomy: 5 Unified Clusters

| Cluster | Source Frameworks | Core Mechanism |
|---------|------------------|----------------|
| **Denial** | FLICC: Fake Experts; CARDS: Trend/Attribution skepticism; 4D: Deny | Reject factual claims |
| **Doubt-Casting** | FLICC: Logical Fallacies, Cherry Picking; CARDS: Science unreliable; 4D: Deceive | Undermine confidence |
| **Deflection** | CARDS: Fossil fuels necessary; 4D: Deflect | Shift responsibility |
| **Delay** | CARDS: Policies harmful, Clean energy bad; 4D: Delay | Oppose current action |
| **Conspiracy** | FLICC: Conspiracy Theories; CARDS: Climate movement conspiracy | Attribute to malicious actors |

See `research/taxonomy_mapping.md` for full crosswalk.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS Bedrock access (via UCL Proxy API)

### 1. Backend Setup
```bash
cd E:/UCL-Workspaces/climate-disinformation

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-core.txt

# Configure environment
cp .env.example .env.bedrock
# Edit .env.bedrock with your BEDROCK_TEAM_ID and BEDROCK_API_TOKEN

# Copy bedrock_client.py from art-of-biasing-LLM (already done if repo was set up correctly)

# Start API
cd backend && python api.py
# → Running on http://localhost:5000
```

### 2. Frontend Setup
```bash
cd frontend-react
npm install
npm start
# → Running on http://localhost:3000
```

### 3. Verify Setup
```bash
curl http://localhost:5000/api/health
# → {"status": "ok", "taxonomy_clusters": ["denial", "doubt_casting", ...]}

curl http://localhost:5000/api/taxonomy/clusters
# → {"clusters": [...5 clusters with techniques...]}

python examples/use_climate_dataset.py
# → Runs 5 examples
```

### 4. Generate Dataset
```bash
# Run Notebook 05 to generate climate_disinfo_dataset.json
jupyter lab notebooks/05_prompt_engineering.ipynb
```

---

## Research Workflow

```
notebooks/01_taxonomy_mapping.ipynb
    → Maps FLICC + CARDS + 4D → unified 5 clusters

notebooks/02_dataset_exploration.ipynb
    → Loads and explores ClimateFEVER + CARDS datasets

notebooks/05_prompt_engineering.ipynb
    → Generates climate_disinfo_dataset.json (50 questions × 5 clusters)

notebooks/03_llm_susceptibility.ipynb
    → Runs multi-turn priming experiments, computes drift scores

notebooks/04_counter_messaging_eval.ipynb
    → Evaluates prebunking/debunking quality
```

---

## Research Documentation

| File | Contents |
|------|---------|
| `research/literature_review.md` | 20 annotated papers on climate disinformation and LLMs |
| `research/taxonomy_mapping.md` | FLICC × CARDS × 4D → unified crosswalk |
| `research/datasets_inventory.md` | Available datasets with download instructions |
| `research/methodology.md` | Experimental design, metrics, statistical plan |

---

## API Endpoints

```
GET  /api/health                        Health check
GET  /api/taxonomy/clusters             All 5 clusters with techniques
GET  /api/taxonomy/clusters/<id>        Single cluster detail
POST /api/graph/expand                  Generate disinformation graph
POST /api/graph/expand-node             Run multi-turn evaluation on a node
POST /api/graph/evaluate                Detect disinformation in text
GET  /api/models                        Available Bedrock models
GET  /api/dataset/stats                 Dataset statistics
GET  /api/dataset/entries               Paginated entries (with filters)
GET  /api/dataset/entries/<index>       Single entry
GET  /api/counter/prebunking/<cluster>  Prebunking message
POST /api/counter/debunking             3-step debunking
```

---

## Deployment (Cloud Run)

```bash
# Build and deploy to Cloud Run (Bedrock backend)
gcloud builds submit --config cloudbuild.bedrock.yaml
# Or: gcloud run deploy climate-disinfo --region us-central1 --source .
```

---

## Related Workspace

- `../art-of-biasing-LLM/` — Source workspace: LLM cognitive bias injection and debiasing

---

## References

Cook et al. (2022) · Touzel et al. (2023) · Diggelmann et al. (2020) ·
Luo et al. (2024) · van der Linden et al. (2022) · Lewandowsky et al. (2021)

See `research/literature_review.md` for full bibliography (20 papers).
