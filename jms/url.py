#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


API_URL_MAPPING = {
    'terminal-register': '/api/applications/v1/terminal/',
    'terminal-heartbeat': '/api/applications/v1/terminal/status/',
    'user-auth': '/api/users/v1/auth/',
    'user-assets': '/api/perms/v1/user/%s/assets/',
    'user-asset-groups': '/api/perms/v1/user/%s/asset-groups/',
    'user-asset-groups-assets': '/api/perms/v1/user/my/asset-groups-assets/',
    'assets-of-group': '/api/perms/v1/user/my/asset-group/%s/assets/',
    'my-profile': '/api/users/v1/profile/',
    'system-user-auth-info': '/api/assets/v1/system-user/%s/auth-info/',
    'validate-user-asset-permission':
        '/api/perms/v1/asset-permission/user/validate/',
}
