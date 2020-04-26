import pytest
from application import create_app, db
from tests.db import data as TEST_DATA
from application.models import Washer, Dryer
pytest.register_assert_rewrite("tests.utils.helpers")


@pytest.fixture(scope="session")
def app():
    _app = create_app()
    _app.app.config["TESTING"] = True
    _app.app.port = 5000

    with _app.app.app_context():
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

    return _app.app
