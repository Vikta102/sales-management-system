from app import create_app
from extensions import db


def test_health_endpoint():
    app = create_app("test")
    with app.app_context():
        db.create_all()

    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json["status"] == "ok"

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
