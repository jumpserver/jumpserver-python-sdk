# -*- coding: utf-8 -*-
#
import paramiko

from .exception import ResponseError, RequestError
from .utils import ssh_key_string_to_obj, get_logger
from .models import Asset, SystemUser, Domain, CommandFilterRule

logger = get_logger(__file__)


class AssetsMixin:
    def get_assets(self):
        try:
            resp = self.http.get('asset-list')
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 200:
            assets = Asset.from_multi_json(resp.json())
            return assets
        else:
            return None

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
        获取系统用户
        :param user_id:
        :return:
        """
        try:
            resp = self.http.get('system-user', pk=user_id)
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 200:
            system_user = SystemUser.from_json(resp.json())
            return system_user
        else:
            return None

    def get_system_user_cmd_filter_rules(self, system_user_id):
        try:
            resp = self.http.get('system-user-cmd-filter-rule-list', pk=system_user_id)
        except (RequestError, RequestError):
            return None

        if resp.status_code == 200:
            rules = CommandFilterRule.from_multi_json(resp.json())
            return rules
        else:
            return None

    def get_system_user_auth_info(self, system_user, asset=None):
        """获取系统用户的认证信息(或获取对应某个的资产的认证信息): 密码, ssh私钥"""
        try:
            if asset is None:
                resp = self.http.get('system-user-auth-info',
                                     pk=system_user.id)
            else:
                resp = self.http.get('system-user-asset-auth-info',
                                     pk=(system_user.id, asset.id))

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
            resp = self.http.get('token-asset', pk=token)
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 200:
            return resp.json()

    def get_domain_detail_with_gateway(self, domain_id):
        try:
            resp = self.http.get('domain-detail', params={"gateway": "1"}, pk=domain_id)
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 200:
            return Domain.from_json(resp.json())

