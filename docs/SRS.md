# Software Requirements Specification (SRS) — TuneTrail

**Project:** TuneTrail – AI-Powered Music Recommendation Mini Platform  
**Course:** AI in Software Engineering (Modules 1–5 & 28-Day Handbook)  
**Version:** 1.0.0

---

## 1. Introduction (Module 1: AI in Software Engineering)

### 1.1 Purpose
TuneTrail solves music discovery fatigue by combining **Content-Based Filtering** (genre, artist, tags, and audio characteristics) with **Collaborative Filtering** (user-user listening similarity) in a configurable **Hybrid Recommendation Engine**.

### 1.2 SDLC Process Model Comparison

| SDLC Model | Strengths | Limitations | Fit for TuneTrail |
| :--- | :--- | :--- | :--- |
| **Waterfall** | Clear milestones, strong documentation | Rigid; late feedback on ML quality | Used only for initial SRS baseline |
| **Incremental** | Delivers working slices per module | Requires clean interfaces upfront | Fits backend -> ML -> UI delivery |
| **Spiral** | Explicit risk analysis (e.g., cold-start, bias) | Higher planning overhead | Guided ML risk & privacy reviews |
| **Prototype** | Rapid UI/UX validation | Throwaway code risk if undisciplined | Used for dashboard & player UX |
| **V-Model** | 1:1 mapping of phases to test levels | Less flexible for evolving AI tuning | Guided unit/integration/E2E mapping |

### 1.3 AI-Driven SDLC vs Traditional SDLC
- **Traditional SDLC:** Manual requirement elicitation, boilerplate coding, and post-hoc test writing.
- **AI-Driven SDLC (Applied in TuneTrail):** AI-assisted requirement decomposition, automated schema & REST scaffolding, AI-generated edge-case unit tests (e.g., cold-start & foreign-key tests), and automated code quality review—paired with human architectural verification.

---

## 2. Functional Requirements

- **FR-1 User Management:** Register, login, logout, profile updates, password hashing (`Werkzeug`), and signed token + session authentication.
- **FR-2 Music Library:** Browse 60+ tracks, search by title/artist/tags, filter by genre and artist, sort by popularity/title/artist/year/tempo, and toggle favourites.
- **FR-3 Playlist Management:** Create playlists, add/remove tracks, view playlist contents, and delete playlists.
- **FR-4 Listening History:** Record play events (`user_id`, `track_id`, timestamp, duration, completion) and display recently played tracks.
- **FR-5 AI Recommendation Engine:** Support `hybrid`, `content`, and `collaborative` modes, configurable weight `α ∈ [0, 1]`, cold-start fallback via user preferences, anti-repetition of recently played tracks, artist/genre diversity, and human-readable explanations.
- **FR-6 Dashboard:** Display total tracks, playlists, favourites, plays, genre distribution, listening activity timeline, recently played tracks, and personalized AI picks.

## 3. Non-Functional Requirements

- **NFR-1 Security:** Passwords hashed at rest; no plaintext credentials or secrets committed; parameterized SQL queries prevent SQL injection.
- **NFR-2 Performance:** Recommendation inference completes in < 100 ms for catalog sizes up to 1,000 tracks.
- **NFR-3 Accessibility & UX:** Dark navy/black theme with purple & teal accents, semantic HTML landmarks, keyboard navigation, and responsive layout.
- **NFR-4 Quality Targets:** >= 80% automated test coverage, >= 50% Hit Rate@10 on held-out plays, 0 blocker defects, green CI/CD pipeline.

---

## 4. AI Prompt Log (Module 1 Artifact)

| Step | Prompt Focus | Outcome & Verification |
| :--- | :--- | :--- |
| P1 | Database schema design for 7 normalized SQLite tables | Verified PKs, FKs, `ON DELETE CASCADE`, and CHECK constraints via `test_foreign_key_constraint_enforced`. |
| P2 | Hybrid Content-Based + Collaborative recommender with cold-start | Verified via `recommendation_engine/evaluator.py` (91.67% Hit Rate@10) and unit tests. |
| P3 | Accessible dark-theme React UI with native `<dialog>` & `aria-live` | Verified via `vite build` and Selenium E2E browser test. |
| P4 | Pytest unit, integration, and coverage suite | Verified 12/12 passing tests and 91% statement coverage. |
