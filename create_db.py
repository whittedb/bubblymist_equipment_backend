from app import create_app, db
from alembic.config import Config
from alembic import command

# Create the initial database
app = create_app()
ctx = app.app.app_context()
ctx.push()
db.create_all()
ctx.pop()

# load the Alembic configuration and generate the
# version table, "stamping" it with the most recent rev:
alembic_cfg = Config("./alembic/alembic.ini")
command.stamp(alembic_cfg, "head")
