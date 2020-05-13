import re
from pathlib import Path

envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
result = {}

location = Path("../environments")
file_to_open = location / "bme_equipment_backend"
with open(file_to_open) as ins:
    for line in ins:
        match = envre.match(line)
        if match is not None:
            result[match.group(1)] = match.group(2)

with open("environment") as out:
    for k, v in result:
        out.write("export set {}={}".format(k, v))
