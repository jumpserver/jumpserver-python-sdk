# -*- coding: utf-8 -*-
#

from cachetools import cached, TTLCache

from .exception import ResponseError, RequestError
from .models import Asset
from .request import Http


class PermsMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    def validate_user_asset_permission(self, user_id, asset_id, system_user_id):
        """验证用户是否有登录该资产的权限"""
        params = {
            'user_id': user_id,
            'asset_id': asset_id,
            'system_user_id': system_user_id,
        }
        r, content = self.http.get(
            'validate-user-asset-permission', use_auth=True, params=params
        )
        if r.status_code == 200:
            return True
        else:
            return False

    @cached(TTLCache(maxsize=100, ttl=60))
    def get_user_assets(self, user):
        """获取用户被授权的资产列表
        [{'hostname': 'x', 'ip': 'x', ...,
         'system_users_granted': [{'id': 1, 'username': 'x',..}]
        ]
        """
        try:
            resp = self.http.get('user-assets', pk=user.id, use_auth=True)
        except (RequestError, ResponseError):
            return []

        if resp.status_code == 200:
            assets = Asset.from_multi_json(resp.json())
            return assets
        else:
            return []

    def get_user_asset_groups(self, user):
        """获取用户授权的资产组列表
        [{'name': 'x', 'comment': 'x', 'assets_amount': 2}, ..]
        """
        try:
            resp = self.http.get('user-asset-groups', pk=user.id, use_auth=True)
        except (ResponseError, RequestError):
            return []

        if resp.status_code == 200:
            asset_groups = content
        else:
            asset_groups = []
        asset_groups = [asset_group for asset_group in asset_groups]
        return asset_groups

    def get_user_asset_groups_assets(self, user):
        """获取用户授权的资产组列表及下面的资产
        [{'name': 'x', 'comment': 'x', 'assets': []}, ..]
        """
        r, content = self.http.get('user-asset-groups-assets', pk=user['id'],
                                   use_auth=True)
        if r.status_code == 200:
            asset_groups_assets = content
        else:
            asset_groups_assets = []
        return asset_groups_assets

