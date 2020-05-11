from application import create_app, db
from alembic.config import Config
from alembic import command
from application.models import User

# Create the initial database
app = create_app()
ctx = app.app.app_context()
ctx.push()
db.create_all()
db.session.add(User(google_email="whittedbrad@gmail.com", facebook_email="fb@the-zoo.net", admin=True))
db.session.add(User(google_email="mlwhitted@gmail.com", facebook_email="michilini_10@yahoo.com", admin=False))
db.session.commit()
ctx.pop()

# load the Alembic configuration and generate the
# version table, "stamping" it with the most recent rev:
alembic_cfg = Config("./alembic/alembic.ini")
command.stamp(alembic_cfg, "head")
