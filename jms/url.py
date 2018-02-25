#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


API_URL_MAPPING = {
    'terminal-register': '/api/terminal/v1/terminal/',
    'terminal-access-key': '/api/terminal/v1/terminal/%s/access-key',
    'terminal-heartbeat': '/api/terminal/v1/terminal/status/',
    'session-replay': '/api/terminal/v1/sessions/%s/replay/',
    'session-list': '/api/terminal/v1/sessions/',
    'session-detail': '/api/terminal/v1/sessions/%s/',
    'session-command': '/api/terminal/v1/command/',
    'user-auth': '/api/users/v1/auth/',
    'user-assets': '/api/perms/v1/user/%s/assets/',
    'user-asset-groups': '/api/perms/v1/user/%s/nodes-assets/',
    'user-nodes-assets': '/api/perms/v1/user/%s/nodes-assets/',
    'my-profile': '/api/users/v1/profile/',
    'system-user-auth-info': '/api/assets/v1/system-user/%s/auth-info/',
    'validate-user-asset-permission': '/api/perms/v1/asset-permission/user/validate/',
    'finish-task': '/api/terminal/v1/tasks/%s/',
    'asset': '/api/assets/v1/assets/%s/',
    'system-user': '/api/assets/v1/system-user/%s',
    'user-profile': '/api/users/v1/profile/',
    'terminal-config': '/api/terminal/v1/terminal/config/',
    'token-asset': '/api/users/v1/connection-token/?token=%s',
}
