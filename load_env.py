import os
import re

envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
result = {}
with open("../environments/bme_equipment_backend") as ins:
    for line in ins:
        match = envre.match(line)
        if match is not None:
            result[match.group(1)] = match.group(2)

os.environ.update(result)