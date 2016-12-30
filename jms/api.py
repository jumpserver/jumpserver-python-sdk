#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals, absolute_import
import os
import json
import base64
import logging

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
try:
    from collections import OrderedDotMap
except ImportError:
    OrderedDotMap = dict

import paramiko
import requests
from requests.structures import CaseInsensitiveDict
from dotmap import DotMap

from . import Auth, URL_MAP
from .utils import sort_assets, PKey
from .compat import builtin_str


_USER_AGENT = 'jms-sdk-py'


class Request(object):
    func_map = {
        'get': requests.get,
        'post': requests.post,
        'patch': requests.patch,
        'put': requests.put,
    }

    def __init__(self, url='http://localhost/', method='get', data=None, params=None,
                 headers=None, content_type='application/json', app_name=''):
        self.url = url
        self.method = method
        self.data = data
        self.params = params or {}
        self.result = None

        if isinstance(headers, dict) and not isinstance(headers, CaseInsensitiveDict):
            self.headers = CaseInsensitiveDict(headers)
        else:
            self.headers = {}

        self.headers['Content-Type'] = content_type
        if data is None or not isinstance(data, dict):
            data = {}
        self.data = json.dumps(data)

        if 'User-Agent' not in self.headers:
            if app_name:
                self.headers['User-Agent'] = _USER_AGENT + '/' + app_name
            else:
                self.headers['User-Agent'] = _USER_AGENT

    def request(self):
        self.result = self.func_map.get(self.method)(url=self.url, headers=self.headers,
                                                     data=self.data, params=self.params)
        return self.result


class ApiRequest(object):
    url_map = URL_MAP

    def __init__(self, app_name, endpoint, auth=None):
        self.app_name = app_name
        self._auth = auth
        self.req = None
        self.endpoint = endpoint

    @staticmethod
    def parser_result(result):
        try:
            content = result.json()
        except ValueError:
            logging.warning(result.content)
            content = {'error': 'We only support json response'}
        return result, DotMap({'content': content}).content

    def request(self, path_name=None, pk=None, method='get', use_auth=True,
                data=None, params=None, content_type='application/json'):

        if self.url_map.get(path_name, None):
            path = self.url_map.get(path_name)
            if pk and '%s' in path:
                path = path % pk
        else:
            path = '/'

        url = self.endpoint.rstrip('/') + path
        self.req = req = Request(url, method=method, data=data, params=params,
                                 content_type=content_type, app_name=self.app_name)
        if use_auth:
            if not self._auth:
                raise ValueError('Require auth visit')
            else:
                self._auth.sign_request(req)
        return self.parser_result(req.request())

    def get(self, *args, **kwargs):
        kwargs['method'] = 'get'
        return self.request(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs['method'] = 'post'
        return self.request(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs['method'] = 'put'
        return self.request(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs['method'] = 'path'
        return self.request(*args, **kwargs)


class AppAuthMixin(object):
    def auth(self, access_key_id=None, access_key_secret=None):
        self._auth = Auth(access_key_id=access_key_id,
                          access_key_secret=access_key_secret)
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def auth_from_f(self, f):
        access_key_id, access_key_secret = self.load_access_key_from_f(f)
        self.auth(access_key_id=access_key_id, access_key_secret=access_key_secret)

    @staticmethod
    def save_access_key(access_key_id, access_key_secret, key_path):
        with open(key_path, b'w') as f:
            f.write('{0}:{1}'.format(access_key_id, access_key_secret))

    def load_access_key_from_f(self, f):
        if isinstance(f, builtin_str) and os.path.isfile(f):
            f = open(f)

        for line in f:
            if not line.strip().startswith('#'):
                self.access_key_id, self.access_key_secret = line.strip().split(':')
                break

        if self.access_key_id is None or self.access_key_secret is None:
            raise IOError('Load access key error')
        return self.access_key_id, self.access_key_secret


class AppService(ApiRequest, AppAuthMixin):
    def __init__(self, *args, **kwargs):
        super(AppService, self).__init__(*args, **kwargs)
        self.access_key_id = None
        self.access_key_secret = None

    def terminal_register(self):
        r, content = self.post('terminal-register', data={'name': self.app_name}, use_auth=False)
        if r.status_code == 201:
            self.access_key_id = content.access_key_id
            self.access_key_secret = content.access_key_secret
            is_success = True
        else:
            is_success = False
        return is_success, content

    def terminal_heatbeat(self):
        r, content = self.post('terminal-heatbeat', use_auth=True)
        if r.status_code == 201:
            return True
        else:
            return False

    def get_system_user_auth_info(self, system_user):
        r, content = self.get('system-user-auth-info', pk=system_user.id)
        if r.status_code == 200:
            password = content.password
            private_key_string = content.private_key

            if private_key_string and private_key_string.find('PRIVATE KEY'):
                private_key = PKey.from_string(private_key_string)
            else:
                private_key = None

            if isinstance(private_key, paramiko.PKey) and len(private_key_string.split('\n')) > 2:
                private_key_log_msg = private_key_string.split('\n')[1]
            else:
                private_key_log_msg = 'None'

            logging.debug('Get system user %s password: %s*** key: %s***' %
                         (system_user.username, password[:4], private_key_log_msg))
            return password, private_key
        else:
            logging.warning('Get system user %s password or private key failed' % system_user.name)
            return None, None

    def send_proxy_log(self, data):
        """
        data = {
            "username": data.username,
            "name": data.name,
            "hostname": data.hostname,
            "ip": data.ip,
            "system_user": data.system_user,
            "login_type": data.login_type,
            "was_failed": 1 if data.failed else 0,
            "date_start": data.date_start.strftime("%Y-%m-%d %H:%M:%S"),
        }
        """
        data.date_start = data.date_start.strftime("%Y-%m-%d %H:%M:%S")
        data.was_failed = 1 if data.was_failed else 0

        r, content = self.post('send-proxy-log', data=data, use_auth=True)
        if r.status_code != 201:
            logging.warning('Send proxy log failed: %s' % content)
            return None
        else:
            return content

    def finish_proxy_log(self, data):
        data.date_finished = data.date_finished.strftime('%Y-%m-%d %H:%M:%S')
        data.was_failed = 1 if data.was_failed else 0
        data.is_finished = 1
        proxy_log_id = data.proxy_log_id or 0
        r, content = self.patch('proxy_log_finish', pk=proxy_log_id, data=data)

        if r.status_code != 200:
            logging.warning('Finish proxy log failed: %s' % proxy_log_id)

    def create_command_log(self, command_no, command, output, log_id, datetime):
        if not command:
            return
        if not isinstance(output, bytes):
            output = output.encode('utf-8', 'replace')
        data = {
            'proxy_log': log_id,
            'command_no': command_no,
            'command': command,
            'output': base64.b64encode(output),
            'datetime': datetime.strftime('%Y-%m-%d %H:%M:%S'),
        }
        result, content = self.post('command_log_create', data=data)
        if result.status_code != 201:
            logging.warning('Create command log failed: %s' % content)
            return False
        return True


class UserService(ApiRequest):
    def __init__(self, *args, **kwargs):
        super(UserService, self).__init__(*args, **kwargs)
        self.user = None
        self.token = ''

    def login(self, username=None, password=None,
              public_key=None, login_type=''):
        data = {
            'username': username,
            'password': password,
            'public_key': public_key,
            'login_type': login_type,
        }
        r, content = self.post('user-auth', data=data, use_auth=False)
        if r.status_code == 200:
            self.token = content.token
            self.user = content.user
            self.auth(self.token)
        else:
            logging.warning('User %s auth failed' % username)

    def auth(self, token=None):
        self._auth = Auth(token=token)

    def is_authenticated(self):
        r, content = self.get('my-profile', use_auth=True)
        if r.status_code == 200:
            self.user = content
            return True
        else:
            return False

    def get_my_assets(self):
        r, content = self.get('my-assets', use_auth=True)
        if r.status_code == 200:
            print(content)
            assets = content
        else:
            assets = []

        assets = sort_assets(assets)
        assets = [asset for asset in assets]
        for asset in assets:
            asset.system_users = [system_user for system_user in asset.system_users]
        return assets

    def get_my_asset_groups(self):
        r, content = self.get('my-asset-groups', use_auth=True)
        if r.status_code == 200:
            asset_groups = content
        else:
            asset_groups = []
        asset_groups = [asset_group for asset_group in asset_groups]
        return asset_groups

    def get_user_asset_group_assets(self, asset_group_id):
        r, content = self.get('assets-of-group', use_auth=True, pk=asset_group_id)
        if r.status_code == 200:
            assets = content
        else:
            assets = []
        assets = sort_assets(assets)
        return [asset for asset in assets]


if __name__ == '__main__':
    pass

