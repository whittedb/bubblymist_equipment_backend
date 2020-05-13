import re

envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
result = {}

with open("bm_equipment_backend") as ins:
    for line in ins:
        match = envre.match(line)
        if match is not None:
            result[match.group(1)] = match.group(2)

with open("environment", mode="w") as out:
    for k, v in result.items():
        out.write("export set {}={}\n".format(k, v))
