import re
from sanic import Blueprint
from sanic.response import json, redirect
from sanic.views import HTTPMethodView
from utils.decorators import login_required, login_optional
from utils import tools
from ssr_panel.exceptions import BadRequest
from ssr_panel import app, render
from ssr_panel.models import User

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


class RegisterView(HTTPMethodView):

    async def get(self, request):
        return render('auth/register.html', request)

    async def post(self, request):
        email = request.form.get('email', '').strip().lower()
        passwd = request.form.get('passwd', '')
        repasswd = request.form.get('repasswd', '')

        if not re.compile(r'^[a-z_0-9.-]{1,64}@([a-z0-9-]{1,200}.){1,5}[a-z]{1,6}$').match(email):
            raise BadRequest('邮箱格式不正确')

        if passwd != repasswd:
            raise BadRequest('两次密码不一致')

        if not 6 <= len(passwd) <= 16:
            raise BadRequest('密码长度 6 ～ 16 位')

        users = await User.objects.execute(
            User.select().where(User.email == email).limit(1)
        )
        if len(users) > 0:
            raise BadRequest('邮箱已经被注册了')

        max_port = 1024
        try:
            users = await User.objects.execute(
                User.select().order_by(User.port.desc()).limit(1)
            )
            if users:
                max_port = users[0].port
        except User.DoesNotExist:
            pass

        await User.objects.create(
            User,
            user_name='',
            email=email,
            password=User.hash_password(passwd),
            passwd=tools.random_string(6),
            port=max_port + 1,
            t=0,
            u=0,
            d=0,
            transfer_enable=tools.gb_to_byte(app.config.DEFAULT_TRAFFIC),
            invite_num=app.config.INVITE_NUM,
            ref_by=0,
            is_admin=0,
            reg_ip=request.ip[0]
        )

        return json({'msg': '注册成功'})


auth.add_route(RegisterView.as_view(), '/register')


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
            raise BadRequest('邮箱或者密码错误')

        if not user.verify_password(password):
            raise BadRequest('邮箱或者密码错误')

        request['session']['uid'] = user.id
        return json({'msg': '欢迎回来'})

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

    if pwd != re_pwd:
        raise BadRequest('两次输入不符合')

    if len(pwd) < 6:
        raise BadRequest('密码太短啦')

    user = request['user']
    if not user.verify_password(old_pwd):
        raise BadRequest('旧密码错误')

    user.password = user.hash_password(pwd)
    await User.objects.update(user)

    return json({'msg': '修改成功'})
