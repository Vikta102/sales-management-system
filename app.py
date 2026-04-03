import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from config import Config, TestConfig
from extensions import csrf, db, login_manager, migrate
from models import User
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.products import products_bp
from routes.sales import sales_bp


def _configure_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
    )


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    _configure_logging()

    app = Flask(__name__)
    if config_name == "test":
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    if config_name != "test":
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY is missing. Set it as an environment variable.")
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            raise RuntimeError("DATABASE_URL is missing. Set it as an environment variable.")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(dashboard_bp)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e: CSRFError):
        return render_template("errors/400.html", message=e.description), 400

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    if os.getenv("AUTO_MIGRATE", "").strip() == "1":
        with app.app_context():
            try:
                db.create_all()
            except Exception:
                app.logger.exception("AUTO_MIGRATE failed. Check DATABASE_URL and DB connectivity.")

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    create_app().run(host="0.0.0.0", port=port)
