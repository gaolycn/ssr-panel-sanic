from sanic import Blueprint, response
from utils.decorators import login_optional
from ss_panel import app

home = Blueprint('home', url_prefix='/')


@home.route('/')
@login_optional
async def index(request):
    user = request['user']
    if user:
        return response.redirect(app.url_for('user_panel.index'))
    else:
        return response.redirect(app.url_for('auth.LoginView'))
