from enum import Enum, auto
from flask import abort, current_app
from marshmallow import EXCLUDE
from app import db
from db.models import Machine, Washer, Dryer, MachineType, RepairLog
from models import MachineSchema, WasherSchema, DryerSchema, RepairLogSchema


class ActiveState(Enum):
    all = auto()
    active = auto()
    inactive = auto()


def get_equipment(active_state):
    try:
        if ActiveState[active_state] is ActiveState.all:
            machines = Machine.query.all()
            return MachineSchema(many=True).dump(machines)
        elif ActiveState[active_state] is ActiveState.active:
            machines = Machine.query.filter(Machine.active)
            return MachineSchema(many=True).dump(machines)
        elif ActiveState[active_state] is ActiveState.inactive:
            machines = Machine.query.filter(Machine.active == False)
            return MachineSchema(many=True).dump(machines)
    except KeyError:
        abort(400, "Read type not implemented: {}".format(active_state))


def get_machine_by_id(machine_id):
    machine = db.session.query(Machine).get(machine_id)
    if machine is None:
        abort(404, "Specified machine does not exist")
    return MachineSchema().dump(machine)


def get_washers(active_state):
    try:
        if ActiveState[active_state] is ActiveState.all:
            machines = Washer.query.all()
            return WasherSchema(many=True).dump(machines)
        elif ActiveState[active_state] is ActiveState.active:
            machines = Washer.query.filter(Machine.active)
            return WasherSchema(many=True).dump(machines)
        elif ActiveState[active_state] is ActiveState.inactive:
            machines = Washer.query.filter(Machine.active == False)
            return WasherSchema(many=True).dump(machines)
    except KeyError:
        abort(400, "Read type not implemented: {}".format(active_state))


def get_dryers(active_state):
    try:
        if ActiveState[active_state] is ActiveState.all:
            machines = Dryer.query.all()
            return DryerSchema(many=True).dump(machines)
        elif ActiveState[active_state] is ActiveState.active:
            machines = Dryer.query.filter(Machine.active)
            return DryerSchema(many=True).dump(machines)
        elif ActiveState[active_state] is ActiveState.inactive:
            machines = Dryer.query.filter(Machine.active == False)
            return DryerSchema(many=True).dump(machines)
    except KeyError:
        abort(400, "Read type not implemented: {}".format(active_state))


def create_washer(body):
    machine = _create_machine(body, WasherSchema, Washer, MachineType.Washer)
    return WasherSchema().dump(machine), 200


def update_washer(body):
    machine = _update_machine(body, Washer, MachineType.Washer)
    return WasherSchema().dump(machine), 200


def create_dryer(body):
    machine = _create_machine(body, DryerSchema, Dryer, MachineType.Dryer)
    return DryerSchema().dump(machine), 200


def update_dryer(body):
    machine = _update_machine(body, Dryer, MachineType.Dryer)
    return DryerSchema().dump(machine), 200


def enable_machine(machine_id):
    with current_app.app_context():
        logger = current_app.logger

    # Does the machine exist?
    machine = db.session.query(Machine).get(machine_id)
    if machine is None:
        abort(404, "Specified machine does not exist")

    # Make sure another machine with the same type and number is currently enabled.
    # Only one machine of a specific number can be active at a time
    machines = Machine.query.filter(
        Machine.type == machine.type,
        Machine.number == machine.number
    )
    if len([machine for machine in machines]) > 1:
        abort(409, "Only one {} of that number can be active at a time".format(machine.type.name))

    machine.active = True
    db.session.commit()
    logger.info("Enabled {} {}".format(machine.type.name, machine.number))
    return 200


def disable_machine(machine_id):
    with current_app.app_context():
        logger = current_app.logger

    # Does the machine exist?
    machine = db.session.query(Machine).get(machine_id)
    if machine is None:
        abort(404, "Specified machine does not exist")

    machine.active = False
    db.session.commit()
    logger.info("Disabled {} {}".format(machine.type.name, machine.number))
    return 200


def get_washer_by_number(number):
    washer = Washer.query.filter(
        Washer.number == number,
        Washer.active
    ).one_or_none()
    if washer is None:
        abort(404, "Washer {} was not found".format(number))
    return WasherSchema().dump(washer)


def read_washer_by_number_include_disabled(number):
    machine = Washer.query.filter(Washer.number == number).one_or_none()
    if machine is None:
        abort(404, "Washer {} was not found".format(number))
    return WasherSchema().dump(machine)


def get_dryer_by_number(number):
    dryer = Dryer.query.filter(
        Dryer.number == number,
        Dryer.active
    ).one_or_none()
    if dryer is None:
        abort(404, "Dryer {} was not found".format(number))
    return DryerSchema().dump(dryer)


def read_dryer_by_number_include_disabled(number):
    machine = Washer.query.filter(Dryer.number == number).one_or_none()
    if machine is None:
        abort(404, "Dryer {} was not found".format(number))
    return DryerSchema().dump(machine)


def create_repair_log(body):
    with current_app.app_context():
        logger = current_app.logger

    repair_log = RepairLogSchema().load(body)
    machine = Machine.query.filter(Machine.id == repair_log.machine_id).one_or_none()
    if machine is None:
        abort(409, "Failed to create repair log. Specified machine does not exist.")
    db.session.add(repair_log)
    db.session.commit()
    updated_machine = db.session.query(Machine).get(repair_log.machine_id)
    logger.info("Created repair log for {} {}".format(updated_machine.type.name, updated_machine.number))
    return RepairLogSchema().dump(repair_log), 200


def update_repair_log(body):
    with current_app.app_context():
        logger = current_app.logger

    update_info = RepairLogSchema().load(body)
    existing = db.session.query(RepairLog).get(update_info.id)
    if existing is None:
        abort(404, "Repair log does not exist")

    updated = db.session.merge(update_info)
    db.session.commit()
    logger.info("Updated repair log({})".format(updated.id))
    return RepairLogSchema().dump(updated), 200


def delete_repair_log(log_id):
    with current_app.app_context():
        logger = current_app.logger

    repair_log = db.session.query(RepairLog).get(log_id)
    if repair_log is None:
        abort(409, "Specified repair log does not exist")

    machine = db.session.query(Machine).get(repair_log.machine_id)
    db.session.delete(repair_log)
    db.session.commit()
    logger.info("Deleted repair log for {} {}".format(machine.type.name, machine.number))
    return 200


def _create_machine(body, schema, machine_model, machine_type):
    with current_app.app_context():
        logger = current_app.logger

    number = body["number"]
    existing = db.session.query(machine_model).filter(
        machine_model.type == machine_type,
        machine_model.number == number,
        machine_model.active
    ).one_or_none()
    if existing is not None:
        abort(409, "{} {} already exists".format(machine_type.name, number))

    machine = schema(unknown=EXCLUDE, exclude=("type",), partial=("active", "type", "id"), dump_only=("id",)).load(body)
    db.session.add(machine)
    db.session.commit()
    logger.info("Created {} {}".format(machine_type.name, machine.number))
    return machine


def _update_machine(body, machine_model, machine_type):
    with current_app.app_context():
        logger = current_app.logger

    machine_id = body["id"]
    existing = db.session.query(machine_model).get(machine_id)
    if existing is None:
        abort(404, "{} does not exist".format(machine_type.name))

    log_message = "Updated {} {}".format(machine_type.name, existing.number)
    if existing.number != body["number"]:
        number_match_machine = machine_model.query.filter(
            machine_model.number == body["number"],
            machine_model.type == machine_type
        ).one_or_none()
        if number_match_machine is not None:
            abort(409, "{} with that number already exists".format(machine_type.name))

        existing.number = body["number"]
        log_message = "Updated {} {} -> {}".format(machine_type.name, existing.number, body["number"])

    existing.serial = body["serial"]
    existing.model = body["model"]
    if "active" in body.keys():
        existing.active = body["active"]
    db.session.commit()

    logger.info(log_message)
    return existing