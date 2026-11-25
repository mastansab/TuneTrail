# Testing & Monitoring Report — TuneTrail (Module 4)

**Project:** TuneTrail – AI-Powered Music Recommendation Mini Platform  
**Test Framework:** Pytest 9.1.1, pytest-cov 7.1.0, Selenium 4.54.0 (Headless Microsoft Edge)

---

## 1. Test Strategy & Prioritization
1. **Priority 1 (Critical):** Authentication, password hashing, SQLite foreign key integrity, and Hybrid Recommendation accuracy/cold-start handling.
2. **Priority 2 (High):** REST API integration for tracks, favourites, playlists, listening history, and dashboard aggregation.
3. **Priority 3 (End-to-End):** Selenium browser automation verifying login, dashboard rendering, library search, playback recording, and AI recommendation studio.

---

## 2. Executed Test Results (Observed)

Command executed:
```bash
python -m pytest tests/unit tests/integration tests/selenium -v --cov=backend --cov=recommendation_engine --cov=database --cov-report=term-missing
```

| Test Suite | Test Cases | Passed | Failed | Skipped |
| :--- | :---: | :---: | :---: | :---: |
| Unit (`tests/unit/test_auth_and_db.py`) | 4 | 4 | 0 | 0 |
| Unit (`tests/unit/test_recommendation_engine.py`) | 4 | 4 | 0 | 0 |
| Integration (`tests/integration/test_api_endpoints.py`) | 4 | 4 | 0 | 0 |
| Selenium E2E (`tests/selenium/test_e2e_ui.py`) | 1 | 1 | 0 | 0 |
| **Total** | **13** | **13** | **0** | **0** |

### Code Coverage Summary
- **Total Statements:** 901
- **Missed:** 69
- **Total Statement Coverage:** **92%** (Target: >= 80%)

---

## 3. Offline AI Recommendation Evaluation (Held-Out Plays)

Command executed: `python -m recommendation_engine.evaluator`

| Metric | Target | Measured Result |
| :--- | :---: | :---: |
| Users Evaluated (with >= 5 plays) | — | 12 |
| **Hit Rate@10** | >= 50.0% | **91.67%** (`0.9167`) |
| **Precision@10** | — | **14.17%** (`0.1417`) |
| **Recall@10** | — | **70.83%** (`0.7083`) |
| **Catalog Coverage** | — | **76.67%** (`0.7667`) |
| **Avg Genre Diversity (Top-10)** | — | **4.25 genres** |

---

## 4. Defect Log

| ID | Description | Root Cause | Resolution | Status |
| :--- | :--- | :--- | :--- | :--- |
| DEF-01 | `pandas` / `sklearn` Cython `.pyd` DLLs blocked by Windows Smart App Control on local host | Unsigned Cython binaries under Python 3.14 | Implemented pure-Python + NumPy TF-IDF, StandardScaler, and Cosine Similarity in `recommendation_engine/` | Closed |
| DEF-02 | `sqlite3.PARSE_DECLTYPES` deprecation warning on Python 3.14 | Legacy adapter in `database/db.py` | Removed `detect_types=sqlite3.PARSE_DECLTYPES`; timestamps serialized as strings | Closed |
| DEF-03 | Selenium E2E read login `<h1>` before async login completed | `visibility_of_element_located` matched `"Welcome back"` | Updated wait to `EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Listener Dashboard")` | Closed |

---

## 5. Continuous Monitoring
- **Health Endpoint:** `GET /api/health` returns database connectivity, track count, and user count.
- **In-App QA Panel:** `Profile & QA` tab displays live `/api/health` status and `/api/recommendations/evaluate` metrics.
