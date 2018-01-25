#!coding: utf-8
#
# from __future__ import unicode_literals
#
import hashlib
import logging
import re
import os
import threading
import base64
import calendar
import time
import datetime
from io import StringIO

import paramiko
import pyte
import pytz
from email.utils import formatdate


try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty


def ssh_key_string_to_obj(text, password=None):
    key = None
    try:
        key = paramiko.RSAKey.from_private_key(StringIO(text), password=password)
    except paramiko.SSHException:
        pass

    try:
        key = paramiko.DSSKey.from_private_key(StringIO(text), password=password)
    except paramiko.SSHException:
        pass
    return key


# def ssh_pubkey_gen(private_key=None, username='jumpserver', hostname='localhost'):
#     if isinstance(private_key, str):
#         private_key = ssh_key_string_to_obj(private_key)
#
#     if not isinstance(private_key, (paramiko.RSAKey, paramiko.DSSKey)):
#         raise IOError('Invalid private key')
#
#     public_key = "%(key_type)s %(key_content)s %(username)s@%(hostname)s" % {
#         'key_type': private_key.get_name(),
#         'key_content': private_key.get_base64(),
#         'username': username,
#         'hostname': hostname,
#     }
#     return public_key
#
#
# def ssh_key_gen(length=2048, type='rsa', password=None,
#                 username='jumpserver', hostname=None):
#     """Generate user ssh private and public key
#
#     Use paramiko RSAKey generate it.
#     :return private key str and public key str
#     """
#
#     if hostname is None:
#         hostname = os.uname()[1]
#
#     f = StringIO()
#
#     try:
#         if type == 'rsa':
#             private_key_obj = paramiko.RSAKey.generate(length)
#         elif type == 'dsa':
#             private_key_obj = paramiko.DSSKey.generate(length)
#         else:
#             raise IOError('SSH private key must be `rsa` or `dsa`')
#         private_key_obj.write_private_key(f, password=password)
#         private_key = f.getvalue()
#         public_key = ssh_pubkey_gen(private_key_obj, username=username, hostname=hostname)
#         return private_key, public_key
#     except IOError:
#         raise IOError('These is error when generate ssh key.')


def content_md5(data):
    """计算data的MD5值，经过Base64编码并返回str类型。

    返回值可以直接作为HTTP Content-Type头部的值
    """
    if isinstance(data, str):
        data = hashlib.md5(data.encode('utf-8'))
    value = base64.b64encode(data.hexdigest().encode('utf-8'))
    return value.decode('utf-8')


_STRPTIME_LOCK = threading.Lock()
_GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
_ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"


def to_unixtime(time_string, format_string):
    with _STRPTIME_LOCK:
        return int(calendar.timegm(time.strptime(str(time_string), format_string)))


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


def make_signature(access_key_secret, date=None):
    if isinstance(date, bytes):
        date = bytes.decode(date)
    if isinstance(date, int):
        date_gmt = http_date(date)
    elif date is None:
        date_gmt = http_date(int(time.time()))
    else:
        date_gmt = date

    data = str(access_key_secret) + "\n" + date_gmt
    return content_md5(data)


def get_logger(filename):
    return logging.getLogger('jms.'+filename)