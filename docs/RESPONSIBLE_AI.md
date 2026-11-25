# Responsible AI & Ethical Development Report — TuneTrail (Module 5)

**Project:** TuneTrail – AI-Powered Music Recommendation Mini Platform

---

## 1. Privacy Protection
- **Data Minimization:** TuneTrail collects only username, email, display name, password hash, and in-app music interactions (plays, favourites, playlists, genre preferences). No sensitive PII, location, or third-party tracking is stored.
- **Credential Security:** Passwords are salted and hashed using `werkzeug.security.generate_password_hash`. Authentication uses signed timed tokens (`itsdangerous.URLSafeTimedSerializer`) and HTTP-only session cookies.
- **No Exposed Secrets:** `.env` and `*.db` are excluded via `.gitignore`; `.env.example` provides safe template defaults.

## 2. Bias, Fairness & Filter Bubble Mitigation
- **Popularity Bias Mitigation:** Pure popularity ranking favors mainstream tracks. TuneTrail combines TF-IDF metadata + audio features with user-user similarity and applies an artist/genre diversity penalty (`0.82 ** artist_count * 0.92 ** genre_count`) so emerging artists and diverse genres appear in top-K recommendations.
- **Cold-Start Fairness:** New users with fewer than 2 listening events (e.g., `newbie` in the seeded dataset) are never given empty results; `HybridRecommender` detects `cold_start=True` and smoothly shifts `effective_alpha = 1.0` to Content-Based Filtering seeded by explicit `UserPreferences`.
- **Anti-Repetition:** Recently played tracks (`avoid_recent_count = 5`) are excluded by default to prevent echo-chamber repetition.

## 3. Transparency & Explainability
Every recommended track surfaces:
- **Match %** and **component scores** (`content` score vs `collaborative` score).
- **Human-readable explanation** (e.g., *"Matches your taste in artist Midnight Pulse & Synthwave genre • Enjoyed by 3 listeners with similar taste"*).
- **Interactive user control** over recommendation mode (`Hybrid`, `Content-Based`, `Collaborative`), weight `α`, and recency exclusion.

## 4. Responsible AI Checklist

| Principle | Status | Evidence |
| :--- | :--- | :--- |
| Synthetic / Non-infringing Dataset | Verified | 60 synthetic tracks in `datasets/tracks.json` |
| Explainable Recommendations | Verified | `explanation`, `reasons`, and `scores` returned by `/api/recommendations` |
| Cold-Start Handling | Verified | Tested on `newbie` user (`effective_alpha = 1.0`) |
| Diversity & Anti-Repetition | Verified | Avg 4.25 distinct genres per top-10 list in offline evaluation |
| Privacy & Password Hashing | Verified | `test_password_hashing_and_verification` |

## 5. AI Usage Declaration
AI coding assistance was used during the SDLC for requirement structuring, boilerplate scaffolding, test-case ideation, and documentation drafting. All algorithms, database constraints, security controls, and evaluation metrics were executed and verified locally against real test runs.
