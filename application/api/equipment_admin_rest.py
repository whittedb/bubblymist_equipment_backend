from flask import abort, current_app
from application import create_app, db
from alembic.config import Config
from alembic import command
from application.models import User
from application.models import Machine


def delete_machine(machine_id):
    with current_app.app_context():
        logger = current_app.logger

    machine = db.session.query(Machine).get(machine_id)
    if machine is None:
        abort(404, "Machine does not exist")

    db.session.delete(machine)
    db.session.commit()
    logger.debug("Deleted {} {}".format(machine.type.name, machine.number))
    return 200


def create_db(body):
    """
    Create the initial DB tables and users
    """
    db.create_all()
    db.session.add(User(google_email="whittedbrad@gmail.com", facebook_email="fb@the-zoo.net", admin=True))
    db.session.add(User(google_email="mlwhitted@gmail.com", facebook_email="michilini_10@yahoo.com", admin=False))
    db.session.commit()

    # load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    alembic_cfg = Config("./alembic/alembic.ini")
    command.stamp(alembic_cfg, "head")
    return 200
