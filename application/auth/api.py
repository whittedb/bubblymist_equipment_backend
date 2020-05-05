import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from facebook import GraphAPI, GraphAPIError
from flask import current_app, abort, jsonify, make_response
import jwt
from connexion import request
from ..models import User, RefreshTokenRequest
from . import GOOGLE_CLIENT_ID, FACEBOOK_CLIENT_ID
from application import db


def master_key_auth(key, **kwargs):
    master_key = "MUINxyUUB3lMH4r1vIkZUSCroUGQ_J6DF9jNF0axEIE"
    if key == master_key:
        return {
            "active": True,
            "sub": "admin"
        }

    # finally, return None if both methods did not login the user
    return None


# Login route authentication hook
# Token is provided from connexion layer
def login_auth(token, **kwargs):
    if token:
        google_email = None
        facebook_email = None
        try:
            # Attempt validation of token against Google credentials
            id_info = _validate_google_auth(token)

            # ID token is valid. Check email against database
            google_email = id_info["email"]
        except ValueError as google_error:
            # Attempt validation of token against Facebook credentials
            try:
                id_info = _validate_facebook_auth(token)

                # ID token is valid. Check email against database
                facebook_email = id_info["email"]
            except GraphAPIError as fb_error:
                # Error accessing Facebook graph API
                current_app.logger.info("Problem with authorization token: {},{}".format(google_error, fb_error))
                return None

        query_param = User.google_email if google_email is not None else User.facebook_email
        query_value = google_email if google_email is not None else facebook_email
        user = User.query.filter(query_param == query_value).one_or_none()
        if user:
            return {
                "sub": user.id
            }

    return None


# API route token authentication hook
# Token is provided from connexion layer
def api_auth(token, **kwargs):
    if token is None:
        abort(401, "Invalid token supplied")

    # Since there is no way to override the OpenAPI 3 root security with a None value, we'll do a hack
    # to ignore the /refresh route
    if request.path.endswith("/refresh") or request.path.endswith("/logout"):
        return {"sub": 0}

    try:
        # Verify that this token was issued by us
        decoded = jwt.decode(token, current_app.secret_key,
                             audience=["equipment.access.bubblymist.com", "equipment.refresh.bubblymist.com"],
                             algorithms="HS256")
        return {
            "sub": decoded["sub"]
        }
    except jwt.ExpiredSignatureError:
        current_app.logger.warn("API token expired")
    except jwt.InvalidSignatureError:
        current_app.logger.warn("Invalid token signature")
    except Exception as e:
        current_app.logger.error("Unhandled exception: {}".format(e))

    return None


# Login using the user ID stashed in the thread local global from the token authentication hook
def login(**kwargs):
    user_id = kwargs["user"]
    access_token, expiry = _generate_access_token(user_id)
    refresh_token, refresh_expiry = _generate_refresh_token(user_id)
    user = db.session.query(User).get(user_id)
    if user is not None:
        user.refresh_token = refresh_token
        db.session.commit()
        resp = make_response(jsonify(access_token=access_token, expiry=expiry))
        _set_refresh_token(resp, refresh_token, refresh_expiry)
        current_app.logger.debug("Refresh: {}".format(refresh_token))
        return resp
    else:
        abort(405)


def logout(**kwargs):
    resp = make_response(jsonify(access_token="", refresh_token=""))
    # Force cookie to expire
    resp.set_cookie("refresh_token", "expire",
                    expires=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                    httponly=True)
    return resp


# Refresh API token
def refresh(**kwargs):
    try:
        refresh_token = request.cookies["refresh_token"]
        current_app.logger.debug("Old Refresh: {}".format(refresh_token))

        # Verify the JWT before proceeding
        jwt.decode(refresh_token, current_app.secret_key,
                   audience="equipment.refresh.bubblymist.com", algorithms="HS256")

        user = User.query.filter(User.refresh_token == refresh_token).one_or_none()
        if user is None:
            # Refresh token not associated to a current user. Phishing attempt?
            current_app.logger.debug("Refresh token not associated with a user")
            abort(401)
        else:
            # Generate a new access token and refresh token
            access_token, expiry = _generate_access_token(user.id)
            refresh_token, refresh_expiry = _generate_refresh_token(user.id)
            user.refresh_token = refresh_token
            db.session.commit()
            resp = make_response(jsonify(access_token=access_token, expiry=expiry))
            _set_refresh_token(resp, refresh_token, refresh_expiry)

            current_app.logger.debug("New Refresh: {}".format(refresh_token))

            return resp
    except KeyError:
        current_app.logger.debug("No refresh token cookie")
        abort(401)
    except jwt.ExpiredSignatureError:
        # Refresh token has expired, caller must re-authenticate
        current_app.logger.debug("Refresh token has expired")
        abort(401)
    except jwt.InvalidAudienceError:
        # Not for us
        current_app.logger.debug("Refresh token has wrong audience")
        abort(401)


# Validate a Google user credentials object
def _validate_google_auth(token):
    # Specify the CLIENT_ID of the app that accesses the backend:
    id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

    # Or, if multiple clients access the backend server:
    # idinfo = id_token.verify_oauth2_token(token, requests.Request())
    # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     raise ValueError('Could not verify audience.')

    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer.')

    return id_info


# Validate a Facebook user credentials object
def _validate_facebook_auth(token):
    profile = GraphAPI(token).get_object("me", **dict({"scope": "email", "fields": "id,name,email"}))
    return profile


def _generate_access_token(user_id):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    return jwt.encode({
        "iss": "equipment.accounts.bubblymist.com",
        "exp": expiry,
        "iat": datetime.datetime.utcnow(),
        "aud": "equipment.access.bubblymist.com",
        "sub": user_id
    }, current_app.secret_key, algorithm="HS256").decode("ascii"), expiry


def _generate_refresh_token(user_id):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return jwt.encode({
        "iss": "equipment.accounts.bubblymist.com",
        "exp": expiry,
        "iat": datetime.datetime.utcnow(),
        "aud": "equipment.refresh.bubblymist.com",
        "sub": user_id
    }, current_app.secret_key, algorithm="HS256").decode("ascii"), expiry


def _set_refresh_token(response, refresh_token, expiry):
    response.set_cookie("refresh_token", refresh_token,
                        expires=datetime.datetime.utcnow() + datetime.timedelta(days=7),
                        httponly=True)
