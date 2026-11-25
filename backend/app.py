"""Flask application factory and entry point for TuneTrail."""

from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.favourites_routes import favourites_bp
from backend.routes.health_routes import health_bp
from backend.routes.history_routes import history_bp
from backend.routes.playlists_routes import playlists_bp
from backend.routes.recommendations_routes import recommendations_bp
from backend.routes.tracks_routes import tracks_bp
from database.seed import seed_database


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the TuneTrail Flask application."""
    static_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    app = Flask(
        __name__,
        static_folder=str(static_dist) if static_dist.exists() else None,
        static_url_path="/",
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    if not app.config.get("TESTING"):
        seed_database(app.config["DATABASE_PATH"], force=False)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tracks_bp)
    app.register_blueprint(favourites_bp)
    app.register_blueprint(playlists_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(dashboard_bp)

    @app.get("/")
    def index():
        if app.static_folder and (Path(app.static_folder) / "index.html").exists():
            return app.send_static_file("index.html")
        return jsonify({
            "service": "TuneTrail AI Music Recommendation API",
            "health": "/api/health",
        }), 200

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=False)
