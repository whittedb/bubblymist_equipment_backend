EQUIPMENT = {
    "Washer1": dict(number=1, description="4 Loader", model="WCAD40KCB-12US", serial="21208000545445", active=True),
    "Washer2": dict(number=2, description="3 Loader", model="WCAD30KCB-12US", serial="21208000545444", active=True),
    "Washer3": dict(number=3, description="2 Loader", model="WCAD20KCB-12US", serial="21208000545446", active=False),
    "Washer4": dict(number=4, description="4 Loader", model="WCAD40KCB-12US", serial="WCAD40KCB-12US", active=True),
    "Dryer1": dict(number=1, description="50 Stack", model="DDBD50KCW-65US", serial="serd1", active=True),
    "Dryer2": dict(number=2, description="30 Stack", model="DDAD30KCW-65US", serial="serd2", active=True),
    "Dryer3": dict(number=3, description="30 Single", model="DCTD30KCW-10US", serial="serd3", active=False),
    "Dryer4": dict(number=4, description="50 Stack", model="DDBD50KCW-65US", serial="serd2", active=True),
}

REPAIR_LOGS = {
    "Washer1": [
        dict(
            date="2020-04-01",
            description="Replace drain valve",
            labor_cost=152.60,
            machine_id=1,
            part_cost=62.55,
            part_name="Drain Valve",
            part_number="DV20"
        ),
        dict(
            date="2020-04-05",
            description="Replace supply valve diaphragm",
            labor_cost=0,
            machine_id=1,
            part_cost=2.55,
            part_name="Supply Valve Diaphragm",
            part_number="Diaphragm"
        )
    ],
    "Washer2": [
        dict(
            date="2020-03-01",
            description="Replace door solenoid",
            labor_cost=0,
            machine_id=2,
            part_cost=42.55,
            part_name="Door Solenoid",
            part_number="DS"
        ),
        dict(
            date="2020-03-05",
            description="Replace supply valve diaphragm",
            labor_cost=0,
            machine_id=2,
            part_cost=2.55,
            part_name="Supply Valve Diaphragm",
            part_number="Diaphragm"
        ),
        dict(
            date="2020-03-15",
            description="Replace motor",
            labor_cost=0,
            machine_id=2,
            part_cost=502.55,
            part_name="Motor",
            part_number="MOT40"
        )
    ]
}


class Counts(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


counts = Counts(**dict(
    total=len(EQUIPMENT.keys()),
    washers=len([k for k in EQUIPMENT.keys() if "Washer" in k]),
    dryers=len([k for k in EQUIPMENT.keys() if "Dryer" in k]),
    active_machines=len([k for k, v in EQUIPMENT.items() if v["active"]]),
    active_washers=len([k for k, v in EQUIPMENT.items() if "Washer" in k and v["active"]]),
    active_dryers=len([k for k, v in EQUIPMENT.items() if "Dryer" in k and v["active"]]),
    inactive_machines=len([k for k, v in EQUIPMENT.items() if not v["active"]]),
    inactive_washers=len([k for k, v in EQUIPMENT.items() if "Washer" in k and not v["active"]]),
    inactive_dryers=len([k for k, v in EQUIPMENT.items() if "Dryer" in k and not v["active"]])
))
