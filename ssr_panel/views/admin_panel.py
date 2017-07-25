import re
from sanic.views import HTTPMethodView
from sanic.response import json
from sanic import Blueprint
from peewee import fn
from python_paginate.web.sanic_paginate import Pagination
from utils import tools
from utils.decorators import admin_required
from ssr_panel.exceptions import BadRequest
from ssr_panel import render
from ssr_panel.models import User, SS_Node, SP_Config

admin_panel = Blueprint('admin_panel', url_prefix='/admin')


@admin_panel.route('/')
@admin_required
async def index_view(request):
    user = request['user']
    analytics = {
        'total_user': await User.objects.count(User.select()),
        'checkin_user': await User.objects.count(User.select().where(User.last_check_in_time > 0)),
        'traffic_usage': tools.flow_auto_show(await User.objects.scalar(User.select(fn.Sum(User.u + User.d)))),
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

        return json({'msg': '更新成功'})

admin_panel.add_route(ConfigView.as_view(), '/config')


class NodeView(HTTPMethodView):
    decorators = [admin_required]

    async def get(self, request):
        user = request['user']
        nodes = await SS_Node.objects.execute(SS_Node.select())
        return render('admin_panel/node/index.html', request, user=user, nodes=nodes)

    async def post(self, request):
        if not request.form.get('name'):
            raise BadRequest('请输入节点名称')
        if not request.form.get('server'):
            raise BadRequest('节点地址错误')
        if not request.form.get('traffic_rate'):
            raise BadRequest('流量比例错误')

        await SS_Node.objects.create(
            SS_Node,
            name=request.form.get('name'),
            type=request.form.get('type'),
            server=request.form.get('server'),
            node_class=request.form.get('node_class'),
            node_group=request.form.get('node_group'),
            traffic_rate=request.form.get('traffic_rate'),
            info=request.form.get('info'),
            note=request.form.get('note'),
            status=request.form.get('status'),
            offset=request.form.get('offset'),
            sort=request.form.get('sort'),
        )
        return json({'msg': '节点添加成功'})

admin_panel.add_route(NodeView.as_view(), '/nodes')


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


class UserView(HTTPMethodView):
    decorators = [admin_required]

    async def get(self, request, user_id):
        user = request['user']

        user_detail = await User.objects.get(User.id == user_id)
        return render('admin_panel/user/edit.html', request, user=user, user_detail=user_detail)

    async def put(self, request, user_id):
        password = request.form.get('pass')
        sspwd = request.form.get('passwd')
        pattern = r'^[\w\-\.@#$]{6,16}$'

        if sspwd and not re.match(pattern, sspwd):
            raise BadRequest('SS连接密码不符合规则，只能为6-16位长度，包含数字大小写字母-._@#$')

        try:
            transfer_enable = tools.gb_to_byte(float(request.form.get('transfer_enable', 0)))
        except:
            raise BadRequest('总流量输入错误')

        user_detail = await User.objects.get(User.id == user_id)
        user_detail.email = request.form.get('email', user_detail.email)
        user_detail.port = request.form.get('port', user_detail.port)
        user_detail.passwd = sspwd or user_detail.passwd
        user_detail.transfer_enable = transfer_enable
        user_detail.auto_reset_day = request.form.get('auto_reset_day', 0)
        user_detail.invite_num = request.form.get('invite_num')
        user_detail.protocol = request.form.get('protocol', user_detail.protocol)
        user_detail.obfs = request.form.get('obfs', user_detail.obfs)
        user_detail.method = request.form.get('method', user_detail.method)
        user_detail.custom_method = request.form.get('custom_method', 0)
        user_detail.custom_rss = request.form.get('custom_rss', 0)
        user_detail.user_class = request.form.get('user_class', 0)
        user_detail.node_group = request.form.get('node_group', 0)
        user_detail.enable = request.form.get('enable', 0)
        user_detail.expire_at = request.form.get('expire_at', user_detail.expire_at)
        user_detail.is_admin = request.form.get('is_admin', 0)
        user_detail.ref_by = request.form.get('ref_by', user_detail.ref_by)
        await User.objects.update(user_detail)

        return json({'msg': '更新成功'})

admin_panel.add_route(UserView.as_view(), '/users/<user_id:int>')
