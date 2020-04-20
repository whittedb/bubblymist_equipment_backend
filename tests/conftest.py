import pytest
from app import create_app, db
from tests.db import data as TEST_DATA
from db.models.machines import Washer, Dryer
pytest.register_assert_rewrite("tests.utils.helpers")


@pytest.fixture(scope="session")
def app():
    _app = create_app()
    _app.app.config["TESTING"] = True
    _app.app.port = 5000
    ctx = _app.app.app_context()
    ctx.push()

    s = db.session
    s.execute("DELETE FROM repair_logs")
    s.execute("ALTER TABLE repair_logs AUTO_INCREMENT = 1")
    s.execute("DELETE FROM machine")
    s.execute("ALTER TABLE machine AUTO_INCREMENT = 1")

    for k, v in TEST_DATA.EQUIPMENT.items():
        if "Washer" in k:
            machine = Washer(**v)
        elif "Dryer" in k:
            machine = Dryer(**v)
        else:
            continue
        s.add(machine)
    s.commit()

    yield _app.app

    ctx.pop()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client(use_cookies=True)
