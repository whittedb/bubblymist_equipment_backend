import os

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID", None)

if GOOGLE_CLIENT_ID is None:
    raise Exception("GOOGLE_CLIENT_ID is not defined in the environment")

if FACEBOOK_CLIENT_ID is None:
    pass
#    raise Exception("FACEBOOK_CLIENT_ID is not defined in the environment")
