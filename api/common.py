"""Common API module."""
import constants
import datetime
import hashlib
import flask
import jwt

def encrypt(password):
    """Encrypt a plain text password.

    :param password [str]: plain text password
    :returns [str]: SHA256-encrypted password
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def decode(token):
    """Decode authentication token.

    https://realpython.com/token-based-authentication-with-flask/

    :param token [str]: auth token
    :returns [str]: decoded user identifier (phone number)
    """
    payload = jwt.decode(token, constants.SECRET_KEY)
    return payload['sub']

def parse(name, type, optional=False):
    """Parse request parameter.

    :param name [str]: parameter name
    :param type [type]: type of variable to parse parameter into
    :param optional [bool]: if False, fail if unable to parse parameter
    :returns [any]: converted request parameter
    :raises ValueError: if unable to parse parameter
    """
    param = flask.request.form.get(name)
    if param:
        return type(param)
    elif not optional:
        raise ValueError(f'missing {name} parameter')
    return param

def route(app, url, method, func, auth=True):
    """Create API route.

    Generates routes that direct requests to functions within the application.

    :param app [Flask]: Flask application object
    :param url [str]: url to route request from
    :param method [str]: http method type (GET, POST, etc.)
    :param func [function]: function to route request to
    :param auth [bool]: if True, require authentication token
    """
    app.route(f'{constants.API_ROOT}/{url}',
              methods=[method],
              defaults={'func': func, 'auth': auth})(_call)

def tokenize(user):
    """
    Generate an authentication token.

    https://realpython.com/token-based-authentication-with-flask/

    :param user [User]: user database model to authenticate
    :returns [str]: auth token
    """
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=constants.AUTH_TOKEN_LIFESPAN_SEC),  # expiration date
        'iat': datetime.datetime.utcnow(),  # time created
        'sub': user.phone  # subject
    }
    return jwt.encode(payload, constants.SECRET_KEY, algorithm='HS256')

def _call(func, auth=True):
    """Call API function.

    Gracefully responds to requests that raise exceptions.

    :param func [function]: function to call
    :param auth [bool]: if True, require authentication token
    :returns [tuple[dict, int]]: JSON response via helper functions
    """
    try:
        return _success(func())
    except Exception as error:
        return _failure(error)

def _failure(error):
    """Failed request response.

    Format:
    {
        "response": {
            "error": <error type>,
            "message": <error message>
        },
        "success": false
    }

    https://developer.mozilla.org/docs/Web/HTTP/Status

    :param error [str]: description of error
    :param statusCode [int]: HTTP failure status code
    :returns [tuple[dict, int]]: JSON response in format (response, status code)
    """
    resp = constants.RESPONSE_TEMPLATE.copy()
    resp['success'] = False
    resp['response'] = {}
    resp['response']['error'] = type(error).__name__
    resp['response']['message'] = str(error)
    return resp, 500  # 500 Internal Server Error

def _success(response=None):
    """Successful request response.

    Format:
    {
        "response": <response>,
        "success": true
    }

    :param response [str]: request response
    :returns [tuple[dict, int]]: JSON response in format (response, status code)
    """
    resp = constants.RESPONSE_TEMPLATE.copy()
    if response is not None:
        resp['response'] = response
    return resp, 200  # 200 OK
