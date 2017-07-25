from sanic.response import json
from sanic.exceptions import SanicException
from ssr_panel import app


class BadRequest(SanicException):
    status_code = 400


@app.exception(BadRequest)
def handle_bad_request(request, exception):
    return json({'ret': 0, 'msg': exception.args[0]}, status=exception.status_code)
