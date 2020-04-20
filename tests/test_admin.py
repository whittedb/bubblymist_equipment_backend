import json
import tests.utils.helpers as helpers


import logging.config

with open("logging.json") as config_data:
    json_config = json.load(config_data)
logging.config.dictConfig(json_config)


###############
# tests
###############
def test_admin_delete_by_id(client):
    with client as c:
        new_machine = dict(
            number=1000,
            model="30Stack Admin",
            serial="serd4-Admin"
        )

        # Test creation
        response = helpers.post(c, "/v1/washer", body=new_machine)
        m = response.get_json()
        # Add type and active into our post body so we can compare
        new_machine.update(**dict(type=0, active=True))
        helpers.compare_machine(m, **new_machine)

        # Retrieve created machine
        response = helpers.get(c, "/v1/equipment/{}".format(m["id"]))
        m = response.get_json()
        helpers.compare_machine(m, **new_machine)

        # Test deletion
        helpers.delete(client, "/v1/admin/equipment/{}".format(m["id"]))
        helpers.get(client, "/v1/washer/1000", 404)
        helpers.get(client, "/v1/equipment/{}".format(m["id"]), 404)
