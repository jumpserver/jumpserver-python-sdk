# -*- coding: utf-8 -*-
#

import unittest
from unittest import mock

from jms.perms import PermsMixin


class TestPermsMixin(unittest.TestCase):
    def setUp(self):
        self.service = PermsMixin("http://jumpserver.org")

    def _mock_test(self, func, resp_case, api_name):
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = resp_case
        mock_get = mock.MagicMock()
        mock_get.return_value = mock_resp
        self.service.http.get = mock_get
        mock_user = mock.MagicMock()
        mock_user.id = mock.sentinel
        assets = func(mock_user)
        mock_get.assert_called_with(api_name, pk=mock.sentinel,
                                    use_auth=True)
        self.assertEqual(len(assets), 1)

    def test_get_user_assets(self):
        resp_case = [
            {
                "id": 1,
                "hostname": "testserver",
                "ip": "123.57.183.135",
                "port": 8022,
                "system_users_granted": [
                    {
                        "id": 1,
                        "name": "web",
                        "username": "web",
                        "protocol": "ssh",
                        "auth_method": "P",
                        "comment": ""
                    }
                ],
                "is_inherited": False,
                "is_active": True,
                "system_users_join": "web",
                "comment": ""
            }
        ]
        api_name = 'user-assets'
        self._mock_test(self.service.get_user_assets, resp_case, api_name)

    def test_get_user_asset_groups(self):
        resp_case = [
            {
                "id": 1,
                "assets_granted": [
                    {
                        "id": 1,
                        "hostname": "testserver",
                        "ip": "123.57.183.135",
                        "port": 8022,
                        "system_users_granted": [
                            {
                                "id": 1,
                                "name": "web",
                                "username": "web",
                                "protocol": "ssh",
                                "auth_method": "P",
                                "comment": ""
                            }
                        ],
                        "is_inherited": False,
                        "is_active": True,
                        "system_users_join": "web",
                        "comment": ""
                    }
                ],
                "name": "Default",
                "created_by": "",
                "date_created": "2017-04-04T01:59:21.142000Z",
                "comment": "Default asset group",
                "system_users": []
            }
        ]
        api_name = 'user-asset-groups'
        self._mock_test(self.service.get_user_asset_groups, resp_case, api_name)


if __name__ == '__main__':
    unittest.main()