"""Integration tests for TuneTrail Flask REST API endpoints."""


def _login_demo(client):
    res = client.post(
        "/api/auth/login",
        json={"identifier": "demo@tunetrail.ai", "password": "Demo@1234"},
    )
    assert res.status_code == 200
    token = res.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_and_unauthenticated_guards(client):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "healthy"
    assert health.get_json()["tracks"] == 60

    assert client.get("/api/dashboard").status_code == 401
    assert client.get("/api/recommendations").status_code == 401
    assert client.get("/api/playlists").status_code == 401


def test_register_login_profile_and_logout_flow(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "username": "test_listener",
            "email": "test_listener@example.com",
            "password": "Password123",
            "display_name": "Test Listener",
            "preferred_genres": ["Lo-Fi", "Ambient"],
        },
    )
    assert reg.status_code == 201
    token = reg.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Duplicate registration blocked
    dup = client.post(
        "/api/auth/register",
        json={
            "username": "test_listener",
            "email": "test_listener@example.com",
            "password": "Password123",
        },
    )
    assert dup.status_code == 409

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.get_json()["user"]["username"] == "test_listener"

    upd = client.put(
        "/api/auth/profile",
        headers=headers,
        json={"display_name": "Updated Listener", "hybrid_alpha": 0.75},
    )
    assert upd.status_code == 200
    assert upd.get_json()["user"]["display_name"] == "Updated Listener"
    assert upd.get_json()["preferences"]["hybrid_alpha"] == 0.75

    assert client.post("/api/auth/logout", headers=headers).status_code == 200


def test_tracks_search_filter_favourites_playlists_and_history(client):
    headers = _login_demo(client)

    # Search and filter tracks
    all_tracks = client.get("/api/tracks", headers=headers)
    assert all_tracks.status_code == 200
    assert all_tracks.get_json()["total"] == 60

    synth = client.get("/api/tracks?genre=Synthwave", headers=headers).get_json()["tracks"]
    assert len(synth) >= 8
    assert all(t["genre"] == "Synthwave" for t in synth)

    search_res = client.get("/api/tracks?q=Neon", headers=headers).get_json()["tracks"]
    assert any("Neon" in t["title"] for t in search_res)

    meta = client.get("/api/tracks/meta").get_json()
    assert "Synthwave" in meta["genres"]
    assert len(meta["artists"]) >= 20

    # Favourites add & remove
    track_id = synth[0]["id"]
    assert client.post("/api/favourites", headers=headers, json={"track_id": track_id}).status_code == 201
    favs = client.get("/api/favourites", headers=headers).get_json()["favourites"]
    assert any(f["id"] == track_id for f in favs)
    assert client.delete(f"/api/favourites/{track_id}", headers=headers).status_code == 200

    # Playlist CRUD
    pl_res = client.post(
        "/api/playlists",
        headers=headers,
        json={"name": "CI Test Playlist", "description": "Created in integration test"},
    )
    assert pl_res.status_code == 201
    pl_id = pl_res.get_json()["playlist"]["id"]

    assert client.post(f"/api/playlists/{pl_id}/tracks", headers=headers, json={"track_id": track_id}).status_code == 201
    assert client.delete(f"/api/playlists/{pl_id}/tracks/{track_id}", headers=headers).status_code == 200
    assert client.delete(f"/api/playlists/{pl_id}", headers=headers).status_code == 200

    # Listening history
    play_res = client.post(
        "/api/history",
        headers=headers,
        json={"track_id": track_id, "play_duration_sec": 210, "completed": True},
    )
    assert play_res.status_code == 201
    hist = client.get("/api/history?limit=5", headers=headers).get_json()["history"]
    assert hist[0]["id"] == track_id


def test_recommendations_and_dashboard_endpoints(client):
    headers = _login_demo(client)

    for mode in ("hybrid", "content", "collaborative"):
        res = client.get(f"/api/recommendations?mode={mode}&limit=8", headers=headers)
        assert res.status_code == 200
        body = res.get_json()
        assert len(body["recommendations"]) == 8
        assert body["meta"]["mode"] == mode

    assert client.get("/api/recommendations?mode=invalid", headers=headers).status_code == 400

    eval_res = client.get("/api/recommendations/evaluate", headers=headers)
    assert eval_res.status_code == 200
    assert eval_res.get_json()["hit_rate_at_k"] >= 0.5

    dash = client.get("/api/dashboard", headers=headers)
    assert dash.status_code == 200
    d = dash.get_json()
    assert d["summary"]["total_tracks"] == 60
    assert len(d["genre_distribution"]) >= 1
    assert len(d["recommendations"]) == 6
