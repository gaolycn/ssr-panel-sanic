import os
from textwrap import dedent
from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from python_paginate.css.semantic import Semantic
from utils import sanic_cookiesession
from utils.peewee_manager import declarative_base
try:
    from config import DEBUG, PORT, WORKERS, SECRET, DB_CONFIG, CHECKIN_TIME, CHECKIN_MIN, CHECKIN_MAX
except ImportError:
    notice = dedent('''
        NOTE: No `config.py` file found.
        `config.py.default` is a template file.
        ''')
    print(notice)

app = Sanic(__name__)


app.config['DEBUG'] = DEBUG
app.config['PORT'] = PORT
app.config['WORKERS'] = WORKERS
app.config['SECRET'] = SECRET
app.config['DB_CONFIG'] = DB_CONFIG
app.config['CHECKIN_TIME'] = CHECKIN_TIME
app.config['CHECKIN_MIN'] = CHECKIN_MIN
app.config['CHECKIN_MAX'] = CHECKIN_MAX

app.config['SESSION_COOKIE_SECRET_KEY'] = SECRET
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_MAX_AGE'] = 3600 * 24 * 15

sanic_cookiesession.setup(app)


os.chdir(os.path.dirname(__file__))
app.static('/static', './static')
app.static('/favicon.ico', './static/images/favicon.ico')
app.static('/robots.txt', './static/robots.txt')


jinja = SanicJinja2(app, enable_async=False, autoescape=True)
render = jinja.render
render_async = jinja.render_async


pagination = {
    '_head': '<ul class="pagination">',
    '_end': '</ul>',
    '_normal': '<li><a href="{href}" rel="prev" style="text-decoration: none">{label}</a></li>',
    '_actived': '<li class="active"><a href="{href}" rel="prev" style="text-decoration: none">{label}</a></li>',
    '_gap': '<li class="disabled"><span>{gap}</span></li>',
    '_prev_label': '<i class="left arrow icon"></i>',
    '_next_label': '<i class="right arrow icon"></i>',
    '_prev_disabled': '<li class="disabled"><span>«</span></li>',
    '_next_disabled': '<li class="disabled"><span>»</span></li>',
    '_prev_normal': '<li><a href="{href}" rel="prev" style="text-decoration: none">«</a></li>',
    '_next_normal': '<li><a href="{href}" rel="prev" style="text-decoration: none">»</a></li>',
    'PER_PAGE': 20,
}

Semantic._head = pagination['_head']
Semantic._end = pagination['_end']
Semantic._normal = pagination['_normal']
Semantic._actived = pagination['_actived']
Semantic._gap = pagination['_gap']
Semantic._prev_label = pagination['_prev_label']
Semantic._next_label = pagination['_next_label']
Semantic._prev_disabled = pagination['_prev_disabled']
Semantic._next_disabled = pagination['_next_disabled']
Semantic._prev_normal = pagination['_prev_normal']
Semantic._next_normal = pagination['_next_normal']
Semantic._next_label = pagination['_next_label']


# unregister the add_flash_to_request middleware
for middleware in list(app.request_middleware):
    if middleware.__name__ == 'add_flash_to_request':
        app.request_middleware.remove(middleware)
        break


# @app.listener('before_server_start')
# async def register_db(app, loop):
#     app.pool = await asyncpg.create_pool(loop=loop, min_size=1, max_size=20, **app.config.DB_CONFIG)


AsyncBaseModel = declarative_base(min_connections=1,
                                  max_connections=20,
                                  **app.config.DB_CONFIG)


# bind routers
from .views import home, auth, user_panel, admin_panel

# register blueprints
app.blueprint(home.home)
app.blueprint(auth.auth)
app.blueprint(user_panel.user_panel)
app.blueprint(admin_panel.admin_panel)
