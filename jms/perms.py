# -*- coding: utf-8 -*-
#

from .exception import ResponseError, RequestError
from .models import Asset, AssetGroup
from .request import Http
from .utils import get_logger

logger = get_logger(__file__)


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
        try:
            resp = self.http.get(
               'validate-user-asset-permission', use_auth=True, params=params
            )
        except (RequestError, ResponseError) as e:
            return False

        if resp.status_code == 200:
            return True
        else:
            return False

    def get_user_assets(self, user):
        """获取用户被授权的资产列表
        [{'hostname': 'x', 'ip': 'x', ...,
         'system_users_granted': [{'id': 1, 'username': 'x',..}]
        ]
        """
        try:
            resp = self.http.get('user-assets', pk=user.id, use_auth=True)
        except (RequestError, ResponseError) as e:
            logger.error("{}".format(e))
            return []

        if resp.status_code == 200:
            assets = Asset.from_multi_json(resp.json())
            return assets
        else:
            return []

    def get_user_asset_groups(self, user):
        """获取用户授权的资产组列表
        [{'name': 'group1', 'comment': 'x', "assets_granted": ["id": "", "],}, ..]
        """
        try:
            resp = self.http.get('user-nodes-assets', pk=user.id, use_auth=True)
        except (ResponseError, RequestError):
            return []

        if resp.status_code == 200:
            asset_groups = AssetGroup.from_multi_json(resp.json())
        else:
            asset_groups = []
        return asset_groups
