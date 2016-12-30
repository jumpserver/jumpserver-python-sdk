#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import hashlib
import threading
import base64
import calendar
import time
from collections import OrderedDict
from email.utils import formatdate

import paramiko
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from .compat import to_string, to_bytes


def b64encode_as_string(data):
    return to_string(base64.b64encode(data))


def content_md5(data):
    """计算data的MD5值，经过Base64编码并返回str类型。

    返回值可以直接作为HTTP Content-Type头部的值
    """
    m = hashlib.md5(to_bytes(data))
    return to_string(base64.b64encode(m.digest()))

_STRPTIME_LOCK = threading.Lock()

_GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
_ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"


def to_unixtime(time_string, format_string):
    with _STRPTIME_LOCK:
        return int(calendar.timegm(time.strptime(time_string, format_string)))


def http_date(timeval=None):
    """返回符合HTTP标准的GMT时间字符串，用strftime的格式表示就是"%a, %d %b %Y %H:%M:%S GMT"。
    但不能使用strftime，因为strftime的结果是和locale相关的。
    """
    return formatdate(timeval, usegmt=True)


def http_to_unixtime(time_string):
    """把HTTP Date格式的字符串转换为UNIX时间（自1970年1月1日UTC零点的秒数）。

    HTTP Date形如 `Sat, 05 Dec 2015 11:10:29 GMT` 。
    """
    return to_unixtime(time_string, _GMT_FORMAT)


def iso8601_to_unixtime(time_string):
    """把ISO8601时间字符串（形如，2012-02-24T06:07:48.000Z）转换为UNIX时间，精确到秒。"""
    return to_unixtime(time_string, _ISO8601_FORMAT)


def http_to_unixtime(time_string):
    """把HTTP Date格式的字符串转换为UNIX时间（自1970年1月1日UTC零点的秒数）。

    HTTP Date形如 `Sat, 05 Dec 2015 11:10:29 GMT` 。
    """
    return to_unixtime(time_string, "%a, %d %b %Y %H:%M:%S GMT")


def make_signature(access_key_secret, date=None):
    if isinstance(date, int):
        date_gmt = http_date(date)
    elif date is None:
        date_gmt = http_date(int(time.time()))
    else:
        date_gmt = date

    data = str(access_key_secret) + "\n" + date_gmt
    return content_md5(data)


def split_string_int(s):
    """Split string or int

    example: test-01-02-db => ['test-', '01', '-', '02', 'db']
    """
    string_list = []
    index = 0
    pre_type = None
    word = ''
    for i in s:
        if index == 0:
            pre_type = int if i.isdigit() else str
            word = i
        else:
            if pre_type is int and i.isdigit() or pre_type is str and not i.isdigit():
                word += i
            else:
                string_list.append(word.lower() if not word.isdigit() else int(word))
                word = i
                pre_type = int if i.isdigit() else str
        index += 1
    string_list.append(word.lower() if not word.isdigit() else int(word))
    return string_list


def sort_assets(assets, order_by='hostname'):
    if order_by == 'hostname':
        key = lambda asset: split_string_int(asset['hostname'])
        assets = sorted(assets, key=key)
    elif order_by == 'ip':
            assets = sorted(assets, key=lambda asset: [int(d) for d in asset['ip'].split('.') if d.isdigit()])
    else:
        key = lambda asset: asset.__getitem__(order_by)
        assets = sorted(assets, key=key)
    return assets


class PKey(object):
    def __init__(self, key_string):
        self.key_string = key_string

    @property
    def pkey(self):
        try:
            pkey = paramiko.RSAKey(file_obj=StringIO.StringIO(self.key_string))
            return pkey
        except paramiko.SSHException:
            try:
                pkey = paramiko.DSSKey(file_obj=StringIO.StringIO(self.key_string))
                return pkey
            except paramiko.SSHException:
                return None

    @classmethod
    def from_string(cls, key_string):
        return cls(key_string=key_string).pkey