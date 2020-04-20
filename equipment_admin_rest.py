from flask import abort, current_app
from db import db
from db import models
import models


def delete_machine(machine_id):
    with current_app.app_context():
        logger = current_app.logger

    machine = db.session.query(models.Machine).get(machine_id)
    if machine is None:
        abort(404, "Machine does not exist")

    db.session.delete(machine)
    db.session.commit()
    logger.info("Deleted {} {}".format(machine.type.name, machine.number))
    return 200
