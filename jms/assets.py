# -*- coding: utf-8 -*-
#
import logging
import paramiko

from .exception import ResponseError, RequestError
from .request import Http
from .utils import PKey


class AssetsMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    def get_system_user_auth_info(self, system_user):
        """获取系统用户的认证信息: 密码, ssh私钥"""
        try:
            resp = self.http.get('system-user-auth-info',
                                 pk=system_user['id'])
        except (RequestError, ResponseError):
            return None, None

        if resp.status_code == 200:
            password = resp.json()['password'] or None
            private_key_string = resp.json()['private_key'] or None

            if private_key_string and private_key_string.find('PRIVATE KEY'):
                private_key = PKey.from_string(private_key_string)
            else:
                private_key = None

            if isinstance(private_key, paramiko.PKey) \
                    and len(private_key_string.split('\n')) > 2:
                private_key_log_msg = private_key_string.split('\n')[1]
            else:
                private_key_log_msg = 'None'

            logging.debug('Get system user %s password: %s*** key: %s***' %
                          (system_user['username'], password[:4],
                           private_key_log_msg))
            return password, private_key
        else:
            logging.warning('Get system user %s password or private key failed'
                            % system_user['username'])
            return None, None
