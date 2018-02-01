# -*- coding: utf-8 -*-
#
import paramiko

from .exception import ResponseError, RequestError
from .request import Http
from .utils import ssh_key_string_to_obj, get_logger
from .models import Asset, SystemUser

logger = get_logger(__file__)


class AssetsMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    def get_asset(self, asset_id):
        """
        获取用户资产
        :param asset_id: 
        :return: 
        """
        try:
            resp = self.http.get('asset', pk=asset_id)
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 200:
            asset = Asset.from_json(resp.json())
            return asset
        else:
            return None

    def get_system_user(self, user_id):
        """
              获取用户资产
              :param user_id:
              :return:
              """
        try:
            resp = self.http.get('system-user', pk=user_id)
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 200:
            asset = SystemUser.from_json(resp.json())
            return asset
        else:
            return None

    def get_system_user_auth_info(self, system_user):
        """获取系统用户的认证信息: 密码, ssh私钥"""
        try:
            resp = self.http.get('system-user-auth-info',
                                 pk=system_user.id)
        except (RequestError, ResponseError):
            return None, None

        if resp.status_code == 200:
            password = resp.json()['password'] or None
            private_key_string = resp.json()['private_key'] or None

            if private_key_string and private_key_string.find('PRIVATE KEY'):
                private_key = ssh_key_string_to_obj(private_key_string, password)
            else:
                private_key = None

            if isinstance(private_key, paramiko.PKey) \
                    and len(private_key_string.split('\n')) > 2:
                private_key_log_msg = private_key_string.split('\n')[1]
            else:
                private_key_log_msg = 'None'

            if password:
                password_log_msg = password[:4]
            else:
                password_log_msg = 'None'

            logger.debug('Get system user {} password: {}*** key: {}***'.format(
                system_user.username, password_log_msg, private_key_log_msg
            ))
            return password, private_key
        else:
            logger.warning('Get system user %s password or private key failed'
                           % system_user.username)
            return None, None

    def get_token_asset(self, token):
        """获取token 所含的系统用户的认证信息: 密码, ssh私钥"""
        try:
            resp = self.http.get('token-asset',
                                  pk=token)
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 200:
            return resp
