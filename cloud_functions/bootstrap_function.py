import json


def get_core_node(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    ip = 'IP OF THE CORE MESSAGE NODE'
    data = {"ip": ip, "port": 1024}
    return json.dumps(data)