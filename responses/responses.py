from marshmallow import Schema, fields


class Response(object):
    def __init__(self, status_code=200, detail=""):
        self.status_code = status_code
        self.detail = detail

    def __repr__(self):
        return "{}, {}".format(self.status_code, self.detail)


class ResponseSchema(Schema):
    status_code = fields.Integer()
    detail = fields.String()
