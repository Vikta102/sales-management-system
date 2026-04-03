import os


def _normalize_database_url(url: str | None) -> str | None:
    if not url:
        return None
    # Railway and Heroku historically used postgres:// which SQLAlchemy rejects.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    # Prefer psycopg (v3) driver for broad Python compatibility.
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
