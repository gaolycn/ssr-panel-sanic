from sanic.views import HTTPMethodView
from sanic.response import json
from sanic import Blueprint
from peewee import fn
from python_paginate.web.sanic_paginate import Pagination
from utils import ss_tool
from utils.decorators import admin_required
from ss_panel import render
from ss_panel.models import User, SS_Node, SP_Config

admin_panel = Blueprint('admin_panel', url_prefix='/admin')


@admin_panel.route('/')
@admin_required
async def index_view(request):
    user = request['user']
    analytics = {
        'total_user': await User.objects.count(User.select()),
        'checkin_user': await User.objects.count(User.select().where(User.last_check_in_time > 0)),
        'traffic_usage': ss_tool.flow_auto_show(await User.objects.scalar(User.select(fn.Sum(User.u + User.d)))),
        'online_user': await User.objects.count(User.select().where(User.t > 3600)),
        'total_node': await SS_Node.objects.count(SS_Node.select()),
    }
    return render('admin_panel/index.html', request, user=user, **analytics)


class ConfigView(HTTPMethodView):
    decorators = [admin_required]

    async def get(self, request):
        user = request['user']
        configs = {}
        for config in await SP_Config.objects.execute(SP_Config.select()):
            configs[config.key] = config.value
        return render('admin_panel/config.html', request, user=user, configs=configs)

    async def put(self, request):
        keys = {
            'analytics-code': 'analyticsCode',
            'home-code': 'homeCode',
            'app-name': 'appName',
            'user-index': 'userIndex',
            'user-node': 'userNode',
        }
        for config in await SP_Config.objects.execute(SP_Config.select()):
            key = keys.get(config.key, '')
            config.value = request.form.get(key, '')
            await SP_Config.objects.update(config)

        res = {'ret': 1, 'msg': '更新成功'}
        return json(res)

admin_panel.add_route(ConfigView.as_view(), '/config')


@admin_panel.route('/nodes')
@admin_required
async def nodes_view(request):
    user = request['user']
    nodes = await SS_Node.objects.execute(SS_Node.select())
    return render('admin_panel/node/index.html', request, user=user, nodes=nodes)


@admin_panel.route('/nodes/create')
@admin_required
async def nodes_create_view(request):
    user = request['user']
    nodes = await SS_Node.objects.execute(SS_Node.select())
    return render('admin_panel/node/create.html', request, user=user, nodes=nodes)


@admin_panel.route('/nodes/<node_id:int>')
@admin_required
async def nodes_edit_view(request, node_id):
    user = request['user']
    node = await SS_Node.objects.get(SS_Node.id == node_id)
    return render('admin_panel/node/edit.html', request, user=user, node=node)


@admin_panel.route('/users')
@admin_required
async def users_view(request):
    user = request['user']

    total = await User.objects.count(User.select())

    page, per_page, offset = Pagination.get_page_args(request)

    users = await User.objects.execute(
        User.select()
            .order_by(User.id.asc())
            .paginate(page, per_page)
    )

    Pagination._per_page = 20
    pagination = Pagination(request, total=total, record_name='users')
    return render('admin_panel/user/index.html', request, user=user, users=users,
                  pagination=pagination)


@admin_panel.route('/users/<user_id:int>')
@admin_required
async def users_edit_view(request, user_id):
    user = request['user']

    user_detail = await User.objects.get(User.id == user_id)
    return render('admin_panel/user/edit.html', request, user=user, user_detail=user_detail)
