from db import db
from enum import Enum


class MachineType(Enum):
    """Type of machine - Washer = 0, Dryer = 1
    """
    Washer = 0
    Dryer = 1


class Machine(db.Model):
    __tablename__ = "machine"
    id = db.Column(db.Integer, primary_key=True)
    repair_logs = db.relationship("RepairLog", back_populates="machine")
    type = db.Column(db.Enum(MachineType), nullable=False)
    description = db.Column(db.String(32), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    model = db.Column(db.String(32), nullable=False)
    serial = db.Column(db.String(64))
    active = db.Column(db.Boolean, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "machine",
        "polymorphic_on": type
    }

    def __init__(self, active=True, **kwargs):
        super().__init__(active=active, **kwargs)
        self._active = active if active is not None and isinstance(active, bool) else False

    def __repr__(self):
        return "{}:{}:{}:{}:{}:{}".format(
            self.id, self.type.value, self.number, self.model, self.serial, self.active
        )


class Washer(Machine):
    def __init__(self, **kwargs):
        super().__init__(type=MachineType.Washer, **kwargs)

    __mapper_args__ = {
        "polymorphic_identity": MachineType.Washer
    }


class Dryer(Machine):
    def __init__(self, **kwargs):
        super().__init__(type=MachineType.Dryer, **kwargs)

    __mapper_args__ = {
        "polymorphic_identity": MachineType.Dryer
    }


class RepairLog(db.Model):
    __tablename__ = "repair_logs"
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False)
    machine = db.relationship("Machine", back_populates="repair_logs")
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(128), nullable=False)
    part_name = db.Column(db.String(64), nullable=False)
    part_number = db.Column(db.String(64))
    part_cost = db.Column(db.Numeric(10, 2), default=0)
    labor_cost = db.Column(db.Numeric(10, 2), default=0)
