from enum import Enum
import csv
import glob
import argparse
from application import create_app, db, logger
from application.models import Washer, Dryer, RepairLog


class MachineType(Enum):
    """Type of machine - Washer = 0, Dryer = 1
    """
    Washer = 0
    Dryer = 1


def process_users(cmd_args):
    pass


def process_machines(cmd_args):
    app = create_app()
    ctx = app.app.app_context()
    ctx.push()

    if not cmd_args.dry:
        logger.info("!!!!! Deleting database data !!!!!")
        s = db.session
        s.execute("DELETE FROM repair_logs")
        s.execute("ALTER TABLE repair_logs AUTO_INCREMENT = 1")
        s.execute("DELETE FROM machine")
        s.execute("ALTER TABLE machine AUTO_INCREMENT = 1")
        s.commit()

    repair_info = {
        0: {},
        1: {}
    }

    repair_fnames = glob.glob("{}/{}*.{}".format(cmd_args.location, cmd_args.repair, cmd_args.extension))
    for repair_fname in repair_fnames:
        splits = repair_fname.split("-")
        machine_type = int(splits[1][0:1])
        machine_number = int(splits[1][1:3])
        logger.info("Reading repairs from {}".format(repair_fname))
        with open(repair_fname) as csvfile:
            repair_reader = csv.DictReader(csvfile, delimiter=",")
            repair_list = []
            for row in repair_reader:
                logger.debug(row)
                repair_log = RepairLog(**dict(
                    date=row["Date"],
                    description=row["Description"],
                    part_name=row["Part Name"],
                    part_number=row["Part Number"],
                    part_cost=0 if row["Part Cost"] == "" else float(row["Part Cost"]),
                    labor_cost=0 if row["Labor Cost"] == "" else float(row["Labor Cost"])
                ))
                repair_list.append(repair_log)
            repair_info[machine_type].update({machine_number: repair_list})

    machines_fname = "{}/{}.{}".format(cmd_args.location, cmd_args.machine, cmd_args.extension)
    logger.info("Reading machines from {}".format(machines_fname))
    with open(machines_fname, newline="") as csvfile:
        machine_reader = csv.DictReader(csvfile, delimiter=',')
        machine_cnt = 0
        row_index = 0
        for row in machine_reader:
            logger.debug(row)
            row_index += 1
            if "CAM" in row["Model"]:
                continue
            machine_type = row["Machine Type"]
            data = dict(
                number=int(row["Number"]),
                description=row["Type"],
                model=row["Model"],
                serial=row["Serial #"]
            )
            if machine_type == "Washer":
                machine = Washer(**data)
            else:
                machine = Dryer(**data)

            logger.info("Creating {}".format(machine))
            if not cmd_args.dry:
                db.session.add(machine)
                try:
                    repairs = repair_info[machine.type.value][machine.number]
                    logger.info("===>>> Adding repair logs to {} {}".format(machine.type.name, machine.number))
                    for repair in repairs:
                        machine.repair_logs.append(repair)
                except KeyError:
                    pass
            machine_cnt += 1

        if not cmd_args.dry:
            db.session.commit()

        logger.info("Added {} machines".format(machine_cnt))

    ctx.pop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("location", help="Location of CSV files to read")
    parser.add_argument("-m", "--machine", default="machines", help="Name of machine file")
    parser.add_argument("-r", "--repair", default="machineMaintenance-", help="Base file name of repair log files")
    parser.add_argument("-e", "--extension", default="csv", help="File name extension for files")
    parser.add_argument("-d", "--dry", action="store_true", help="Dry run")
    args = parser.parse_args()
    logger.info(args)
    process_users(args)
    process_machines(args)
    exit(1)
