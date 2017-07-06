import datetime
import time
import hashlib
import peewee
from utils import ss_tool
from ss_panel import app, AsyncBaseModel


METHOD_CHOICES = (
    ('none', 'none'),
    ('table', 'table'),
    ('aes-128-cfb', 'aes-128-cfb'),
    ('aes-192-cfb', 'aes-192-cfb'),
    ('aes-256-cfb', 'aes-256-cfb'),
    ('aes-128-ctr', 'aes-128-ctr'),
    ('aes-192-ctr', 'aes-192-ctr'),
    ('aes-256-ctr', 'aes-256-ctr'),
    ('bf-cfb', 'bf-cfb'),
    ('camellia-128-cfb', 'camellia-128-cfb'),
    ('camellia-192-cfb', 'camellia-192-cfb'),
    ('camellia-256-cfb', 'camellia-256-cfb'),
    ('rc4-md5', 'rc4-md5'),
    ('rc4-md5-6', 'rc4-md5-6'),
    ('salsa20', 'salsa20'),
    ('chacha20', 'chacha20'),
    ('chacha20-ietf', 'chacha20-ietf'),
)

PROTOCOL_CHOICES = (
    ('origin', 'origin'),
    ('verify_deflate', 'verify_deflate'),
    ('auth_sha1_v4_compatible', 'auth_sha1_v4_compatible'),
    ('auth_aes128_md5', 'auth_aes128_md5'),
    ('auth_aes128_sha1', 'auth_aes128_sha1'),
    ('auth_chain_a', 'auth_chain_a'),
)


class User(AsyncBaseModel):
    user_name = peewee.CharField(max_length=128)
    email = peewee.CharField(max_length=128, unique=True)
    password = peewee.CharField(max_length=128)  # 登录密码
    passwd = peewee.CharField(max_length=128)  # SS密码
    t = peewee.IntegerField(default=0)
    u = peewee.BigIntegerField()
    d = peewee.BigIntegerField()
    transfer_enable = peewee.BigIntegerField()
    auto_reset_day = peewee.IntegerField(default=0)
    port = peewee.IntegerField(unique=True)
    switch = peewee.IntegerField(default=1)
    enable = peewee.IntegerField(default=1)
    type = peewee.IntegerField(default=1)
    last_get_gift_time = peewee.IntegerField(default=0)
    last_check_in_time = peewee.IntegerField(default=0)
    last_rest_pass_time = peewee.IntegerField(default=0)
    reg_date = peewee.DateTimeField(default=datetime.datetime.now)
    invite_num = peewee.IntegerField(default=0)
    is_admin = peewee.IntegerField(default=0)
    ref_by = peewee.IntegerField(default=0)
    expire_time = peewee.IntegerField(default=0)
    method = peewee.CharField(max_length=128, choices=METHOD_CHOICES, default='aes-256-cfb')
    custom_method = peewee.IntegerField(default=0)
    custom_rss = peewee.IntegerField(default=0)
    protocol = peewee.CharField(max_length=256, choices=PROTOCOL_CHOICES, default='origin')
    protocol_param = peewee.CharField(max_length=256, null=True)
    obfs = peewee.CharField(max_length=256, default='plain')
    obfs_param = peewee.CharField(max_length=256, null=True)
    user_class = peewee.IntegerField(default=0)
    node_group = peewee.IntegerField(default=0)
    contact = peewee.CharField(max_length=256)
    expire_at = peewee.DateField(default=lambda: datetime.date.today() + datetime.timedelta(days=365*3))
    is_email_verify = peewee.IntegerField(default=0)
    reg_ip = peewee.CharField(max_length=256, default='127.0.0.1')

    @property
    def gravatar(self):
        email_hash = hashlib.md5(self.email.strip().lower().encode('utf-8')).hexdigest()
        return "https://secure.gravatar.com/avatar/%s?d=identicon&r=x" % email_hash

    @property
    def last_ss_time(self):
        if self.t == 0:
            return '从未使用'
        return datetime.datetime.fromtimestamp(self.t)

    @property
    def last_checkin_time(self):
        if self.last_check_in_time == 0:
            return '从未签到'
        return datetime.datetime.fromtimestamp(self.last_check_in_time)

    @property
    def is_able_to_checkin(self):
        last = self.last_check_in_time
        hours = app.config.CHECKIN_TIME
        return last + hours * 3600 < time.time()

    @property
    def traffic_usage_percent(self):
        total = self.u + self.d
        if self.transfer_enable == 0:
            return 0
        return round(total / self.transfer_enable * 100, 2)

    @property
    def enable_traffic(self):
        return ss_tool.flow_auto_show(self.transfer_enable)

    @property
    def enable_traffic_in_gb(self):
        return ss_tool.flow_to_gb(self.transfer_enable)

    @property
    def used_traffic(self):
        total = self.u + self.d
        return ss_tool.flow_auto_show(total)

    @property
    def unused_traffic(self):
        total = self.u + self.d
        return ss_tool.flow_auto_show(self.transfer_enable - total)

    def hash_password(self, password):
        return hashlib.sha256((password + app.config.SECRET).encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self.password == self.hash_password(password)


class UserToken(AsyncBaseModel):
    user = peewee.ForeignKeyField(User, related_name='user_tokens')
    token = peewee.CharField(max_length=512)
    create_time = peewee.IntegerField()
    expire_time = peewee.IntegerField()


class SS_Node(AsyncBaseModel):
    name = peewee.CharField(max_length=256)
    type = peewee.IntegerField()
    server = peewee.CharField(max_length=256)
    method = peewee.CharField(max_length=128, default='aes-256-cfb')
    protocol = peewee.CharField(max_length=256, default='origin')
    protocol_param = peewee.CharField(max_length=256, null=True)
    obfs = peewee.CharField(max_length=256, default='plain')
    obfs_param = peewee.CharField(max_length=256, null=True)
    node_class = peewee.IntegerField(default=0)
    node_group = peewee.IntegerField(default=0)
    traffic_rate = peewee.FloatField(default=1)
    info = peewee.CharField(max_length=256)
    note = peewee.CharField(max_length=256)
    status = peewee.IntegerField(default=1)
    offset = peewee.IntegerField(default=0)
    sort = peewee.IntegerField()


class SsNodeInfoLog(AsyncBaseModel):
    node = peewee.ForeignKeyField(SS_Node, related_name='ss_node_info_logs')
    uptime = peewee.FloatField()
    load = peewee.CharField(max_length=64)
    log_time = peewee.IntegerField()


class SsNodeOnlineLog(AsyncBaseModel):
    node = peewee.ForeignKeyField(SS_Node, related_name='ss_node_online_logs')
    online_user = peewee.IntegerField()
    log_time = peewee.IntegerField()


class SS_Checkin_Log(AsyncBaseModel):
    user = peewee.ForeignKeyField(User, related_name='ss_checkin_logs')
    checkin_at = peewee.IntegerField(default=time.time)
    traffic = peewee.DoubleField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)


class SsPasswordReset(AsyncBaseModel):
    email = peewee.CharField(max_length=64)
    token = peewee.CharField(max_length=256)
    init_time = peewee.IntegerField()
    expire_time = peewee.IntegerField()


class SsInviteCode(AsyncBaseModel):
    user = peewee.ForeignKeyField(User, related_name='ss_invite_codes')
    code = peewee.CharField(max_length=256)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)


class User_Traffic_Log(AsyncBaseModel):
    user = peewee.ForeignKeyField(User, related_name='user_traffic_logs')
    u = peewee.IntegerField()
    d = peewee.IntegerField()
    node = peewee.ForeignKeyField(SS_Node, related_name='user_traffic_logs')
    rate = peewee.FloatField()
    traffic = peewee.CharField(max_length=64)
    log_time = peewee.IntegerField()

    @property
    def total_used(self):
        return ss_tool.flow_auto_show(self.u + self.d)

    @property
    def log_datetime(self):
        return datetime.datetime.fromtimestamp(self.log_time)


class SP_Config(AsyncBaseModel):
    key = peewee.CharField(max_length=256, unique=True)
    value = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)


class SpLog(AsyncBaseModel):
    type = peewee.CharField(max_length=32)
    msg = peewee.TextField()
    created_time = peewee.IntegerField()


class SpEmailVerify(AsyncBaseModel):
    email = peewee.CharField(max_length=64)
    token = peewee.CharField(max_length=128)
    expire_at = peewee.IntegerField()
