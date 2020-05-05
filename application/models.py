from enum import Enum
from marshmallow import post_load
from marshmallow import fields, Schema
from marshmallow_enum import EnumField
from application import db, ma


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


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    google_email = db.Column(db.String(64))
    facebook_email = db.Column(db.String(64))
    refresh_token = db.Column(db.String(512))
    admin = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return "{}:{}:{}:{}".format(self.id, self.google_email, self.facebook_email, self.admin)


class RepairLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RepairLog
        dateformat = "%Y-%m-%d"

    machine_id = ma.Integer()

    @post_load
    def make_repair_log(self, data, **kwargs):
        return RepairLog(**data)


class MachineSchema(ma.SQLAlchemyAutoSchema):
    type = EnumField(Machine, by_value=True)

    class Meta:
        model = Machine
        include_relationships = True

    repair_logs = ma.List(ma.Nested(RepairLogSchema))


class WasherSchema(ma.SQLAlchemyAutoSchema):
    type = EnumField(Machine, by_value=True)

    class Meta:
        model = Washer
        include_relationships = True

    repair_logs = ma.List(ma.Nested(RepairLogSchema))

    @post_load
    def make_machine(self, data, **kwargs):
        return Washer(**data)


class DryerSchema(ma.SQLAlchemyAutoSchema):
    type = EnumField(Machine, by_value=True)

    class Meta:
        model = Dryer
        include_relationships = True
        include_fk = True

    repair_logs = ma.List(ma.Nested(RepairLogSchema))

    @post_load
    def make_machine(self, data, **kwargs):
        return Dryer(**data)


class RefreshToken(object):
    def __init__(self, grant_type, refresh_token):
        self._grant_type = grant_type
        self._refresh_token = refresh_token

    @property
    def grant_type(self):
        return self._grant_type

    @property
    def refresh_token(self):
        return self._refresh_token


class RefreshTokenRequest(Schema):
    grant_type = fields.String()
    refresh_token = fields.String()

    @post_load
    def make_refresh_token(self, data, **kwargs):
        return RefreshToken(**data)
