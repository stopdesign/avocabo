import sys
import time
from datetime import timedelta
from functools import reduce

from constance import config
from django.urls import reverse


def daterange(start_date, end_date, include_last=True):
    assert type(start_date) is type(end_date)
    for n in range(int((end_date - start_date).days) + int(bool(include_last))):
        yield start_date + timedelta(n)


def timeit(func):
    def wrap(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time() - start_time
        print("function [{}] finished in {} ms".format(func.__name__, int(end_time * 1000)))
        return res

    return wrap


def url_to_edit(obj):
    """
    Url to edit object in admin
    """
    return reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])


class temp_disconnect_signal:
    """
    Temporarily disconnect a model from a signal
    """

    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
        )

    def __exit__(self, type, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
        )


def is_running_cmd(cmd, strict=False):
    """
    Детектим что был запущен ./manage.py <cmd>
    """
    try:
        if strict:
            return sys.argv[1] == cmd
        else:
            return sys.argv[1].startswith(cmd)
    except IndexError:
        return False


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_bank_api_headers():
    headers = {
        "Api-Token": getattr(config, "BANK_API_TOKEN", ""),
        "Api-Secret-Key": getattr(config, "BANK_API_SECRET_KEY", ""),
    }
    return headers


def sizeof_fmt(num, suffix="b"):
    format_str = "%3.1f %s%s"
    for unit in ["", "K", "M", "G"]:
        if abs(num) < 1024.0:
            return format_str % (num, unit, suffix)
        num /= 1024.0
    return format_str % (num, "Yi", suffix)


def prod(l):
    """
    перемножает элементы списка друг с другом
    Math.prod появилась только в python 3.8
    """
    return reduce(lambda x, y: x * y, l)
