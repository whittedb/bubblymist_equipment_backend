from enum import Enum
from flask import url_for
from tests.db import data as TEST_DATA
import tests.utils.helpers as helpers


###############
# tests
# The order of these tests matters
###############
class MachineType(Enum):
    Washer = 0
    Dryer = 1


def test_create_repair_logs(client):
    # Test adding a repair log to a non-existent machine
    invalid_test_log = TEST_DATA.REPAIR_LOGS["Washer1"][0].copy()
    invalid_test_log["machine_id"] = 1000
    helpers.post(client, "/v1/repair_log", body=invalid_test_log, status_code=409)

    # Add all the test data repair logs
    for key in TEST_DATA.REPAIR_LOGS:
        cnt = 0
        number = int(key[len(key)-1])
        for test_log in TEST_DATA.REPAIR_LOGS[key]:
            cnt += 1
            response = helpers.post(client, "/v1/repair_log", body=test_log)
            repair_log = response.get_json()
            helpers.compare_repair_log(repair_log, **test_log)

            response = helpers.get(client, "/v1/washer/{}".format(number))
            machine = response.get_json()
            assert len(machine["repair_logs"]) == cnt
            helpers.compare_repair_log(machine["repair_logs"][cnt - 1], **test_log)


def test_get_repair_log(client):
    # Get the washer so we can get the ID of the first repair log
    response = helpers.get(client, "/v1/washer/1")
    machine = response.get_json()
    repair_log_id = machine["repair_logs"][0]["id"]

    # Get repair log by ID and compare it
    response = helpers.get(client, "/v1/repair_log/{}".format(repair_log_id))
    repair_log = response.get_json()
    test_data = TEST_DATA.REPAIR_LOGS["Washer1"][0].copy()
    test_data["id"] = repair_log_id
    helpers.compare_repair_log(repair_log, **test_data)


def test_machine_has_repair_logs(client):
    response = helpers.get(client, "/v1/washer/1")
    washer1 = response.get_json()
    assert len(washer1["repair_logs"]) == len(TEST_DATA.REPAIR_LOGS["Washer1"])
    test_log = TEST_DATA.REPAIR_LOGS["Washer1"][0]
    helpers.compare_repair_log(washer1["repair_logs"][0], **test_log)


def test_get_equipment_all(client):
    response = helpers.get(client, "/v1/equipment_list/all")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.total,
                                   washer_count=TEST_DATA.counts.washers,
                                   dryer_count=TEST_DATA.counts.dryers)


def test_update_repair_log(client):
    # Get the machine
    response = helpers.get(client, "/v1/washer/1")
    machine = response.get_json()

    # Modify the log info, update and compare
    repair_log = machine["repair_logs"][0]
    update_info = repair_log.copy()
    update_info.update(**dict(
        date="1963-01-01",
        description="Update Description",
        part_name="Update Name",
        part_number="Update Part Number",
        part_cost=99.99,
        labor_cost=88.88
    ))
    response = helpers.put(client, "/v1/repair_log", body=update_info)
    updated_log = response.get_json()
    helpers.compare_repair_log(updated_log, **update_info)

    # Retrieve the machine and compare
    response = helpers.get(client, "/v1/washer/1")
    machine = response.get_json()
    repair_log = machine["repair_logs"][0]
    helpers.compare_repair_log(repair_log, **update_info)


def test_delete_repair_log(client):
    # Make sure washer exists
    response = helpers.get(client, "/v1/washer/1")
    machine = response.get_json()
    assert len(machine["repair_logs"]) == len(TEST_DATA.REPAIR_LOGS["Washer1"])

    # Delete the repair log and test that it no longer exists
    log_id = machine["repair_logs"][0]["id"]
    helpers.delete_by_db_id(client, "/v1/repair_log/{}".format(log_id))
    response = helpers.get(client, "/v1/washer/1")
    machine = response.get_json()
    assert len(machine["repair_logs"]) == len(TEST_DATA.REPAIR_LOGS["Washer1"]) - 1
    for repair_log in machine["repair_logs"]:
        assert log_id != repair_log["id"]


def test_get_equipment_active(client):
    response = helpers.get(client, "/v1/equipment_list/active")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.active_machines,
                                   washer_count=TEST_DATA.counts.active_washers,
                                   dryer_count=TEST_DATA.counts.active_dryers)


def test_get_equipment_inactive(client):
    response = helpers.get(client, "/v1/equipment_list/inactive", 200)
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.inactive_machines,
                                   washer_count=TEST_DATA.counts.inactive_washers,
                                   dryer_count=TEST_DATA.counts.inactive_dryers)


def test_get_washers_all(client):
    response = helpers.get(client, "/v1/washer_list/all")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.washers,
                                   washer_count=TEST_DATA.counts.washers,
                                   dryer_count=0)


def test_get_washers_active(client):
    response = helpers.get(client, "/v1/washer_list/active")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.active_washers,
                                   washer_count=TEST_DATA.counts.active_washers,
                                   dryer_count=0)


def test_get_washers_inactive(client):
    response = helpers.get(client, "/v1/washer_list/inactive")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.inactive_washers,
                                   washer_count=TEST_DATA.counts.inactive_washers,
                                   dryer_count=0)


def test_get_machine(client):
    response = helpers.get(client, "/v1/equipment/1")
    washer = response.get_json()
    tm = TEST_DATA.EQUIPMENT["Washer{}".format(1)].copy()
    tm.update({"type": 0, "active": True})
    helpers.compare_machine(washer, **tm)


def test_get_single_washer(client):
    response = helpers.get(client, "/v1/washer/1")
    washer = response.get_json()
    tm = TEST_DATA.EQUIPMENT["Washer{}".format(1)].copy()
    tm.update({"type": 0, "active": True})
    helpers.compare_machine(washer, **tm)


def test_get_dryers_all(client):
    response = helpers.get(client, "/v1/dryer_list/all")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.dryers,
                                   washer_count=0,
                                   dryer_count=TEST_DATA.counts.dryers)


def test_get_dryers_active(client):
    response = helpers.get(client, "/v1/dryer_list/active")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.active_dryers,
                                   washer_count=0,
                                   dryer_count=TEST_DATA.counts.active_dryers)


def test_get_dryers_inactive(client):
    response = helpers.get(client, "/v1/dryer_list/inactive")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.inactive_dryers,
                                   washer_count=0,
                                   dryer_count=TEST_DATA.counts.inactive_dryers)


def test_get_single_dryer(client):
    response = helpers.get(client, "/v1/dryer/1")
    m = response.get_json()
    tm = TEST_DATA.EQUIPMENT["Dryer{}".format(1)].copy()
    tm.update({"type": 1, "active": True})
    helpers.compare_machine(m, **tm)


def test_disable_enable_machine(client):
    # Test both washer and dryer endpoints
    for machine_type in [0, 1]:
        # Get and disable machine
        machine = helpers.enable_machine(client, machine_type, number=1, enable=False)
        machine_id = machine["id"]
        response = helpers.get(client, "/v1/equipment/{}".format(machine_id), 200)
        machine = response.get_json()
        assert not machine["active"]

        # Restore machine to enabled for further tests
        machine = helpers.enable_machine(client, machine_type, machine_id=machine_id)
        assert machine["active"]


def test_disable_create_get_machine_with_same_machine_number(client):
    # Get and disable dryer
    dryer = helpers.enable_machine(client, MachineType.Dryer, number=2, enable=False)
    disabled_dryer_id = dryer["id"]
    assert not dryer["active"]

    # Create a new machine with the same number as the disabled machine
    new_machine_body = dict(
        number=2,
        description="Test create with same number",
        model="2nd Stack",
        serial="2nd Serial"
    )
    response = helpers.post(client, "/v1/dryer", body=new_machine_body)
    new_machine = response.get_json()
    helpers.get(client, "/v1/dryer/2")

    # Delete newly created machine so we can re-enable the disabled machine
    helpers.delete(client, "/v1/admin/equipment/{}".format(new_machine["id"]))

    # Re-enable dryer for further tests
    dryer = helpers.enable_machine(client, MachineType.Dryer, machine_id=disabled_dryer_id)
    assert dryer["active"]


def test_create_dryer(client):
    new_machine = dict(
        number=10,
        description="Test dryer create",
        model="30Stack",
        serial="serd10"
    )

    # Test when active machine already exists
    existing_machine = new_machine.copy()
    existing_machine.update(**dict(number=1))
    helpers.post(client, "/v1/dryer", body=existing_machine, status_code=409)

    # Test creation
    response = helpers.post(client, "/v1/dryer", body=new_machine)
    m = response.get_json()
    # Add type and active into our post body so we can compare
    new_machine.update(**dict(type=1, active=True))
    helpers.compare_machine(m, **new_machine)

    response = helpers.get(client, "/v1/dryer/{}".format(new_machine["number"]))
    m = response.get_json()
    helpers.compare_machine(m, **new_machine)

    response = helpers.get(client, "/v1/equipment_list/all")
    helpers.compare_equipment_list(response,
                                   total_count=TEST_DATA.counts.total+1,
                                   washer_count=TEST_DATA.counts.washers,
                                   dryer_count=TEST_DATA.counts.dryers+1)


def test_update_washer(client):
    _test_update_machine(client, MachineType.Washer)


def test_update_dryer(client):
    _test_update_machine(client, MachineType.Dryer)


def _test_update_machine(c, machine_type):
    assert machine_type in [MachineType.Washer, MachineType.Dryer]

    base_uri = "/v1/washer" if machine_type is MachineType.Washer else "/v1/dryer"

    def uri(suffix=None):
        return base_uri if suffix is None else base_uri + "/{}".format(suffix)

    update_base = dict(
        number=1,
        description="Test update {}".format(machine_type.name),
        model="Updated {} Model".format(machine_type.name),
        serial="Updated {} Serial".format(machine_type.name),
        type=machine_type.value
    )

    response = helpers.get(c, uri(1))
    machine = response.get_json()
    update_base.update(**dict(active=machine["active"]))

    # Test that updating to an existing number returns a 409
    update = update_base.copy()
    update.update(**dict(id=machine["id"]))
    update.update(**dict(number=2))
    helpers.put(c, uri(), 409, body=update)

    # Test update to same number returns 200 and matches
    update = update_base.copy()
    update.update(**dict(id=machine["id"]))
    response = helpers.put(c, uri(), body=update)
    updated_machine = response.get_json()
    update.update(**dict(type=machine_type.value, active=True))
    helpers.compare_machine(updated_machine, **update)

    # Test update to a non existent number returns 200 and matches
    update = update_base.copy()
    update.update(**dict(id=machine["id"], number=5000))
    response = helpers.put(c, uri(), body=update)
    updated_machine = response.get_json()
    update.update(**dict(type=machine_type.value, active=True))
    helpers.compare_machine(updated_machine, **update)

    # Test that updating with a non-existent ID returns 404
    update = update_base.copy()
    update.update(**dict(id=5000))
    helpers.put(c, uri(), 404, body=update)
