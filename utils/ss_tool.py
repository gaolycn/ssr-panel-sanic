import base64


def flow_auto_show(value):
    kb = 1024
    mb = 1048576
    gb = 1073741824
    if abs(value) > gb * 2:
        return '%sGB' % round(float(value) / gb, 2)
    elif abs(value) > mb * 2:
        return '%sMB' % round(float(value) / mb, 2)
    elif abs(value) > kb * 8:
        return '%sKB' % round(float(value) / kb, 2)
    else:
        return '%dB' % value


def flow_to_gb(traffic):
    gb = 1048576 * 1024.0
    return traffic / gb


def to_mb(traffic):
    mb = 1048576
    return traffic * mb


def to_gb(traffic):
    gb = 1048576 * 1024
    return traffic * gb


def base64_url_encode(s):
    return base64.urlsafe_b64encode(s.encode('utf-8')).decode()


def base64_url_decode(s):
    return base64.urlsafe_b64decode(s)


def base64_encode(s):
    return base64.b64encode(s.encode('utf-8')).decode()


def base64_decode(s):
    return base64.b64decode(s)
