import random
import time
import re
import ujson
from sanic import Blueprint
from sanic.response import json
from python_paginate.web.sanic_paginate import Pagination
from utils import ss_tool
from utils.decorators import login_required
from ss_panel import render
from ss_panel.models import User, SS_Node, User_Traffic_Log, SS_Checkin_Log

user_panel = Blueprint('user_panel', url_prefix='/dashboard')


@user_panel.route('/')
@login_required
async def index(request):
    user = request['user']
    return render('user_panel/index.html', request, user=user, checkin_time=request.app.config.CHECKIN_TIME)


@user_panel.route('/nodes')
@login_required
async def nodes(request):
    user = request['user']
    nodes = await SS_Node.objects.execute(
        SS_Node
            .select()
            .where((SS_Node.node_group == user.node_group) | (SS_Node.node_group == 0))
    )
    return render('user_panel/nodes.html', request, user=user, nodes=nodes)


@user_panel.route('/nodes/<node_id:int>')
@login_required
async def node_detail(request, node_id):
    user = request['user']
    node = await SS_Node.objects.get(SS_Node.id == node_id)

    if user.user_class < node.node_class or (user.node_group != node.node_group and node.node_group != 0):
        return json({})

    ss_info = {
        'server': node.server,
        'server_port': user.port,
        'password': user.passwd,
        'method': user.method,
        'protocol': user.protocol,
        'obfs': user.obfs
    }
    if user.obfs in ('http_post', 'http_simple'):
        ss_info['obfs_param'] = user.obfs_param

    if user.obfs in ('http_simple', 'http_post', 'random_head', 'tls1.2_ticket_auth') \
            or user.protocol in ('verify_deflate', 'auth_chain_a', 'auth_sha1_v4',
                                 'auth_aes128_md5', 'auth_aes128_sha1'):

        ss_url = '%s:%s:%s:%s:%s:%s/?obfsparam=%s&remarks=%s' % (
            ss_info['server'],
            ss_info['server_port'],
            user.protocol.replace('_compatible', ''),
            ss_info['method'],
            user.obfs.replace('_compatible', ''),
            ss_tool.base64_url_encode(ss_info['password']),
            ss_tool.base64_url_encode(user.obfs_param),
            ss_tool.base64_url_encode(node.name)
        )
        ssqr_s_n = 'ssr://' + ss_tool.base64_url_encode(ss_url)
        ss_url = '%s:%s:%s:%s@%s:%s/%s' % (
            user.obfs.replace('_compatible', ''),
            user.protocol.replace('_compatible', ''),
            ss_info['method'],
            ss_info['password'],
            ss_info['server'],
            ss_info['server_port'],
            ss_tool.base64_encode(user.obfs_param)
        )
        ssqr_s = "ss://" + ss_tool.base64_encode(ss_url)
        ssqr = ssqr_s
    else:
        ss_url = '%s:%s:%s:%s:%s:%s/?obfsparam=%s&remarks=%s' % (
            ss_info['server'],
            ss_info['server_port'],
            user.protocol.replace('_compatible', ''),
            ss_info['method'],
            user.obfs.replace('_compatible', ''),
            ss_tool.base64_url_encode(ss_info['password']),
            ss_tool.base64_url_encode(user.obfs_param or ''),
            ss_tool.base64_url_encode(node.name)
        )
        ssqr_s_n = "ssr://" + ss_tool.base64_encode(ss_url)
        ss_url = '%s:%s:%s:%s@%s:%s/%s' % (
            user.obfs.replace('_compatible', ''),
            user.protocol.replace('_compatible', ''),
            ss_info['method'],
            ss_info['password'],
            ss_info['server'],
            ss_info['server_port'],
            ss_tool.base64_encode(user.obfs_param or '')
        )
        ssqr_s = "ss://" + ss_tool.base64_encode(ss_url)
        ss_url = '%s:%s@%s:%s' % (
            ss_info['method'],
            ss_info['password'],
            ss_info['server'],
            ss_info['server_port']
        )
        ssqr = "ss://" + ss_tool.base64_encode(ss_url)

    surge_base = '/'.join(request.url.split('/')[:3]) + '/downloads/ProxyBase.conf'
    surge_proxy = '#!PROXY-OVERRIDE:ProxyBase.conf\n'
    surge_proxy += '[Proxy]\n'
    surge_proxy += 'Proxy = custom,%s,%s,%s,%s,%s/downloads/SSEncrypt.module' % (
        ss_info['server'],
        ss_info['server_port'],
        ss_info['method'],
        ss_info['password'],
        '/'.join(request.url.split('/')[:3])
    )

    data = {
        'ss_info': ss_info,
        'ss_info_show': ujson.dumps(ss_info, indent=4),
        'ssqr': ssqr,
        'ssqr_s_n': ssqr_s_n,
        'ssqr_s': ssqr_s,
        'surge_base': surge_base,
        'surge_proxy': surge_proxy
    }
    return render('user_panel/node_detail.html', request, user=user, **data)


@user_panel.route('/profile')
@login_required
async def profile(request):
    user = request['user']
    return render('user_panel/profile.html', request, user=user)


@user_panel.route('/trafficlog')
@login_required
async def traffic_log(request):
    user = request['user']

    total = await User_Traffic_Log.objects.count(
        User_Traffic_Log
            .select()
            .where(User_Traffic_Log.user == user)
    )

    page, per_page, offset = Pagination.get_page_args(request)

    traffic_logs = await User_Traffic_Log.objects.execute(
        User_Traffic_Log
            .select()
            .where(User_Traffic_Log.user == user)
            .order_by(User_Traffic_Log.id.desc())
            .paginate(page, per_page)
    )
    ids = [log.id for log in traffic_logs]

    logs_query = (
        User_Traffic_Log
            .select()
            .where(User_Traffic_Log.id << ids)
            .order_by(User_Traffic_Log.id.desc())
    )

    nodes_query = SS_Node.select()

    traffic_logs = await User_Traffic_Log.objects.prefetch(logs_query, nodes_query)

    Pagination._per_page = 20
    pagination = Pagination(request, total=total, record_name='traffic_logs')
    return render('user_panel/traffic_log.html', request, user=user, traffic_logs=traffic_logs,
                  pagination=pagination)


@user_panel.route('/edit')
@login_required
async def edit(request):
    user = request['user']
    return render('user_panel/edit.html', request, user=user)


@user_panel.route('/invite')
@login_required
async def invite(request):
    user = request['user']
    return render('user_panel/invite.html', request, user=user)


@user_panel.route('/checkin', methods=['POST'])
@login_required
async def checkin(request):
    user = request['user']

    res = {'msg': '签到失败，请稍候再试.', 'ret': 0}
    if not user.is_able_to_checkin:
        res['msg'] = '您似乎已经签到过了...'
        res['ret'] = 1
        return json(res)

    traffic = random.randint(request.app.config.CHECKIN_MIN, request.app.config.CHECKIN_MAX)
    traffic_to_add = ss_tool.to_mb(traffic)

    async with User.objects.atomic():
        user.transfer_enable += traffic_to_add
        user.last_check_in_time = time.time()
        await User.objects.update(user)

        await SS_Checkin_Log.objects.create(SS_Checkin_Log, user=user, traffic=traffic_to_add)

        res['msg'] = '获得了 %s MB流量.' % traffic
        res['ret'] = 1

    return json(res)


@user_panel.route('/ssr_edit', methods=['POST'])
@login_required
async def ssr_edit(request):
    pwd = request.form.get('sspwd', '')
    pattern = r'^[\w\-\.@#$]{6,16}$'

    res = {'ret': 0}
    if not re.match(pattern, pwd):
        res['msg'] = "SS连接密码不符合规则，只能为6-16位长度，包含数字大小写字母-._@#$"
        return json(res)

    user = request['user']
    user.passwd = pwd
    await User.objects.update(user)

    res['ret'] = 1
    return json(res)
