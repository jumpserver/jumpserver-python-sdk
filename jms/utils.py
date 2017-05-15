#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

import hashlib
import re
import threading
import base64
import calendar
import time
import datetime
from io import StringIO

import pyte
import pytz
from email.utils import formatdate

import paramiko
from dotmap import DotMap


try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

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
        date = date.decode("utf-8")
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
        # print(assets)
        # assets = sorted(assets, key=key)
    elif order_by == 'ip':
            assets = sorted(assets, key=lambda asset: [int(d) for d in asset['ip'].split('.') if d.isdigit()])
    else:
        key = lambda asset: asset.__getitem__(order_by)
        assets = sorted(assets, key=key)
    return assets


class PKey(object):
    @classmethod
    def from_string(cls, key_string):
        try:
            pkey = paramiko.RSAKey(file_obj=StringIO(key_string))
            return pkey
        except paramiko.SSHException:
            try:
                pkey = paramiko.DSSKey(file_obj=StringIO(key_string))
                return pkey
            except paramiko.SSHException:
                return None


def from_string(cls, key_string):
    return cls(key_string=key_string).pkey


def timestamp_to_datetime_str(ts):
    datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt = datetime.datetime.fromtimestamp(ts, tz=pytz.timezone('UTC'))
    return dt.strftime(datetime_format)


def to_dotmap(data):
    """将接受dict转换为DotMap"""
    if isinstance(data, dict):
        data = DotMap(data)
    elif isinstance(data, list):
        data = [DotMap(d) for d in data]
    else:
        raise ValueError('Dict or list type required...')
    return data


class MultiQueue(Queue):
    def mget(self, size=1, block=True, timeout=5):
        items = []
        for i in range(size):
            try:
                items.append(self.get(block=block, timeout=timeout))
            except Empty:
                break
        return items


class TtyIOParser(object):
    def __init__(self, width=80, height=24):
        self.screen = pyte.Screen(width, height)
        self.stream = pyte.ByteStream()
        self.stream.attach(self.screen)
        self.ps1_pattern = re.compile(r'^\[?.*@.*\]?[\$#]\s|mysql>\s')

    def clean_ps1_etc(self, command):
        return self.ps1_pattern.sub('', command)

    def parse_output(self, data, sep='\n'):
        output = []
        if not isinstance(data, bytes):
            data = data.encode('utf-8', 'ignore')

        self.stream.feed(data)
        for line in self.screen.display:
            if line.strip():
                output.append(line)
        self.screen.reset()
        return sep.join(output[0:-1])

    def parse_input(self, data):
        command = []
        if not isinstance(data, bytes):
            data = data.encode('utf-8', 'ignore')

        self.stream.feed(data)
        for line in self.screen.display:
            line = line.strip()
            if line:
                command.append(line)
        if command:
            command = command[-1]
        else:
            command = ''
        self.screen.reset()
        command = self.clean_ps1_etc(command)
        return command


def wrap_with_line_feed(s, before=0, after=1):
    return '\r\n' * before + s + '\r\n' * after


def wrap_with_color(text, color='white', background=None, bolder=False, underline=False):
    bolder_ = '1'
    underline_ = '4'
    color_map = {
        'black': '30',
        'red': '31',
        'green': '32',
        'brown': '33',
        'blue': '34',
        'purple': '35',
        'cyan': '36',
        'white': '37',
    }
    background_map = {
        'black': '40',
        'red': '41',
        'green': '42',
        'brown': '43',
        'blue': '44',
        'purple': '45',
        'cyan': '46',
        'white': '47',
    }

    wrap_with = []
    if bolder:
        wrap_with.append(bolder_)
    if underline:
        wrap_with.append(underline_)
    if background:
        wrap_with.append(background_map.get(background, ''))
    wrap_with.append(color_map.get(color, ''))
    return '\033[' + ';'.join(wrap_with) + 'm' + text + '\033[0m'


def wrap_with_warning(text, bolder=False):
    return wrap_with_color(text, color='red', bolder=bolder)


def wrap_with_info(text, bolder=False):
    return wrap_with_color(text, color='brown', bolder=bolder)


def wrap_with_primary(text, bolder=False):
    return wrap_with_color(text, color='green', bolder=bolder)


def wrap_with_title(text):
    return wrap_with_color(text, color='black', background='green')
