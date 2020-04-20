from marshmallow import post_load
from marshmallow_enum import EnumField
from app import ma
from db.models import Machine, Washer, Dryer, RepairLog


class RepairLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RepairLog
        dateformat = "%m/%d/%Y"

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
