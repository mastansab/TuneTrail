# TuneTrail — AI-Powered Music Recommendation Mini Platform

TuneTrail is a full-stack, AI-powered music discovery platform built for the **AI in Software Engineering** course (covering Modules 1–5 and the 28-day project handbook).

## Key Features
- **User Management:** Secure registration, login/logout, password hashing (`Werkzeug`), signed Bearer tokens + Flask sessions, and customizable listener preferences.
- **Music Library:** 60 synthetic tracks across 8 genres (`Synthwave`, `Electronic`, `Lo-Fi`, `Ambient`, `Jazz Fusion`, `Indie Pop`, `Alt Rock`, `R&B Soul`) with search, genre/artist filtering, and sorting.
- **Playlists & Favourites:** Full CRUD for playlists, add/remove tracks via accessible `<dialog>` modal, and favourite track toggling.
- **Listening History & Player Bar:** Persistent bottom player bar that records play events (`ListeningHistory`) and dynamically updates recommendations.
- **Hybrid AI Recommendation Engine:**
  - **Content-Based Filtering:** TF-IDF on genre, artist, album, and tags + standardized audio features (`tempo`, `energy`, `danceability`, `valence`, `acousticness`, `release_year`).
  - **Collaborative Filtering:** User-user cosine similarity over listening history & favourites.
  - **Hybrid Mode:** Configurable `α` weight, automatic cold-start fallback, artist/genre diversity penalty, anti-repetition of recently played tracks, and human-readable explanations.
- **Listener Dashboard & QA Monitoring:** KPIs, genre distribution, listening activity timeline, and live offline Hit Rate@10 evaluation.

---

## Project Structure

```text
TuneTrail/
├── frontend/               # React.js + Vite dark-theme streaming UI
├── backend/                # Flask REST API (Blueprints, Services, Auth)
├── recommendation_engine/  # Content-Based, Collaborative, Hybrid & Evaluator
├── database/               # SQLite schema.sql, db.py, and seed.py
├── datasets/               # Synthetic tracks.json catalog
├── tests/
│   ├── unit/               # Auth, DB, and AI engine unit tests
│   ├── integration/        # Flask REST API integration tests
│   └── selenium/           # Headless browser E2E tests
├── docs/                   # SRS, Architecture, Use Cases, Testing, QA, Responsible AI
├── .github/workflows/      # GitHub Actions CI/CD workflow
├── Dockerfile              # Multi-stage production container
├── docker-compose.yml      # Local container orchestration
├── Jenkinsfile             # Jenkins CI/CD pipeline
├── sonar-project.properties# SonarQube configuration
└── requirements.txt
```

---

## Local Setup & Execution

### 1. Initialize Database & Run Backend (Port 5000)
```bash
cd TuneTrail
pip install -r requirements.txt
python -m database.seed
python -m backend.app
```

### 2. Run Frontend Dev Server (Port 5173)
```bash
cd TuneTrail/frontend
npm install
npm run dev
```
Open **http://localhost:5173** (or **http://localhost:5000** when `frontend/dist` is built via `npm run build`).

**Demo Account:** `demo@tunetrail.ai` / `Demo@1234` (or click **Fill Demo Listener** on the login screen).

---

## Testing & AI Evaluation

```bash
cd TuneTrail
# Unit & Integration Tests + Coverage
python -m pytest tests/unit tests/integration -v --cov=backend --cov=recommendation_engine --cov=database --cov-report=term-missing

# Selenium E2E Browser Test
python -m pytest tests/selenium/test_e2e_ui.py -v

# Offline AI Recommendation Evaluation (Held-out plays)
python -m recommendation_engine.evaluator
```

---

## Docker Execution
```bash
cd TuneTrail
docker compose up --build
```
Then visit **http://localhost:5000**.
