from sanic import Blueprint
from sanic.response import json, redirect
from sanic.views import HTTPMethodView
from utils.decorators import login_required, login_optional
from ss_panel import app, render
from ss_panel.models import User

auth = Blueprint('auth', url_prefix='/auth')

# Register Error Code
WRONG_CODE = 501
ILLEGAL_EMAIL = 502
PASSWORD_TOO_SHORT = 511
PASSWORD_NOT_EQUAL = 512
EMAIL_USED = 521

# Login Error Code
USER_NOT_EXIST = 601
USER_PASSWORD_WRONG = 602

# Verify Email
VERIFY_EMAIL_WRONG_EMAIL = 701
VERIFY_EMAIL_EXIST = 702


@auth.route('/register')
async def register(request):
    return render('auth/register.html', request)


class LoginView(HTTPMethodView):

    async def get(self, request):
        return render('auth/login.html', request)

    async def post(self, request):
        email = request.form.get('email', '').lower()
        password = request.form.get('passwd', '')
        remember_me = request.form.get('remember_me')

        res = {}

        # Handle Login
        try:
            user = await User.objects.get(User.email == email)
        except User.DoesNotExist:
            res['ret'] = 0
            res['error_code'] = USER_NOT_EXIST
            res['msg'] = "邮箱或者密码错误"
            return json(res)

        if not user.verify_password(password):
            res['ret'] = 0
            res['error_code'] = USER_PASSWORD_WRONG
            res['msg'] = "邮箱或者密码错误"
            return json(res)

        request['session']['uid'] = user.id
        return json({"ret": 1, "msg": "欢迎回来"})

auth.add_route(LoginView.as_view(), '/login')


@auth.route('/logout')
@login_optional
async def logout(request):
    if 'uid' in request['session']:
        request['session'].pop('uid')
    return redirect(app.url_for('home.index'))


@auth.route('/reset')
async def reset(request):
    return render('auth/reset.html', request)


@auth.route('/token')
async def token(request):
    return render('auth/token.html', request)


@auth.route('/password', methods=['POST'])
@login_required
async def password(request):
    old_pwd = request.form.get('oldpwd', '')
    pwd = request.form.get('pwd', '')
    re_pwd = request.form.get('repwd', '')

    res = {'ret': 0}

    if pwd != re_pwd:
        res['msg'] = '两次输入不符合'
        return json(res)

    if len(pwd) < 6:
        res['msg'] = '密码太短啦'
        return json(res)

    user = request['user']
    if not user.verify_password(old_pwd):
        res['msg'] = '旧密码错误'
        return json(res)

    user.password = user.hash_password(pwd)
    await User.objects.update(user)

    res['ret'] = 1
    res['msg'] = 'ok'
    return json(res)
