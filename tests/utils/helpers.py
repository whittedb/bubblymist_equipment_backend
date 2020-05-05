import base64
api_key = "MUINxyUUB3lMH4r1vIkZUSCroUGQ_J6DF9jNF0axEIE"
print("API Key: {}\n".format(api_key))


def get(client, uri, status_code=200):
    response = client.get(uri, headers={"X-API-Key": api_key})
    assert response.status_code == status_code
    return response


def post(client, uri, body=None, status_code=200):
    if body is not None:
        response = client.post(uri, json=body, headers={"X-API-Key": api_key})
    else:
        response = client.post(uri)
    assert response.status_code == status_code
    return response


def put(client, uri, status_code=200, body=None):
    response = client.put(uri, json=body, headers={"X-API-Key": api_key})
    assert response.status_code == status_code
    return response


def delete(client, uri, status_code=200):
    response = client.delete(uri, headers={"X-API-Key": api_key})
    assert response.status_code == status_code
    return response


def delete_by_db_id(client, uri, status_code=200):
    response = client.delete(uri, headers={"X-API-Key": api_key})
    assert response.status_code == status_code
    return response


def enable_machine(client, machine_type, number=None, machine_id=None, enable=True):
    if number is not None:
        if machine_type == 0:
            uri = "/v1/washer/{}".format(number)
        else:
            uri = "/v1/dryer/{}".format(number)
    elif machine_id is not None:
        uri = "/v1/equipment/{}".format(machine_id)
    else:
        raise Exception("Missing argument: number or machine_id")

    response = get(client, uri)
    machine = response.get_json()
    machine_id = machine["id"]
    put(client, "/v1/equipment_{}/{}".format("enable" if enable else "disable", machine_id), 200)
    response = get(client, "/v1/equipment/{}".format(machine_id), 200)
    return response.get_json()


def compare_repair_log(repair_log, **kwargs):
    assert repair_log["date"] == kwargs["date"]
    assert repair_log["description"] == kwargs["description"]
    assert repair_log["labor_cost"] == kwargs["labor_cost"]
    assert repair_log["machine_id"] == kwargs["machine_id"]
    assert repair_log["part_cost"] == kwargs["part_cost"]
    assert repair_log["part_name"] == kwargs["part_name"]
    assert repair_log["part_number"] == kwargs["part_number"]


def compare_equipment_list(response, total_count, washer_count, dryer_count):
    assert response.status_code == 200
    machines = response.get_json()
    assert isinstance(machines, list)
    assert len(machines) == total_count
    wcnt = 0
    dcnt = 0
    for m in machines:
        assert "id" in m.keys()
        assert m["id"] != 0
        assert "type" in m.keys()
        assert "number" in m.keys()
        assert "model" in m.keys()
        assert "serial" in m.keys()
        assert "active" in m.keys()
        machine_type = m["type"]
        assert machine_type == 0 or machine_type == 1
        if m["type"] == 0:
            wcnt += 1
        else:
            dcnt += 1
    assert wcnt == washer_count
    assert dcnt == dryer_count


def compare_machine(machine, **kwargs):
    assert machine["type"] == kwargs["type"]
    assert machine["number"] == kwargs["number"]
    assert machine["model"] == kwargs["model"]
    assert machine["serial"] == kwargs["serial"]
    assert machine["active"] == kwargs["active"]
