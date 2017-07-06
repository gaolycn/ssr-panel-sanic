from functools import wraps
from sanic import response
from sanic.request import Request
from ss_panel.models import User


def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                uid = arg.get('session', {}).get('uid')
                if uid is None:
                    return response.redirect(arg.app.url_for('auth.LoginView', next=arg.url))
                try:
                    user = await User.objects.get(User.id == uid)
                    arg['uid'] = uid
                    arg['user'] = user
                except User.DoesNotExist:
                    return response.redirect(arg.app.url_for('auth.LoginView', next=arg.url))
                break
        return await f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                uid = arg.get('session', {}).get('uid')
                if uid is None:
                    return response.redirect(arg.app.url_for('auth.LoginView', next=arg.url))
                try:
                    user = await User.objects.get(User.id == uid, User.is_admin == 1)
                    arg['uid'] = uid
                    arg['user'] = user
                except User.DoesNotExist:
                    return response.redirect(arg.app.url_for('auth.LoginView', next=arg.url))
                break
        return await f(*args, **kwargs)
    return decorated_function


def login_optional(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                uid = arg.get('session', {}).get('uid')
                arg['uid'] = uid
                if uid is not None:
                    try:
                        user = await User.objects.get(User.id == uid)
                        arg['user'] = user
                    except User.DoesNotExist:
                        arg['user'] = None
                else:
                    arg['user'] = None
                break
        return await f(*args, **kwargs)
    return decorated_function
