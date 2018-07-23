#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


API_URL_MAPPING = {
    'terminal-register': '/api/v1/terminal/terminal/',
    'terminal-access-key': '/api/v1/terminal/terminal/%s/access-key',
    'terminal-heartbeat': '/api/v1/terminal/terminal/status/',
    'session-replay': '/api/v1/terminal/sessions/%s/replay/',
    'session-list': '/api/v1/terminal/sessions/',
    'session-detail': '/api/v1/terminal/sessions/%s/',
    'session-command': '/api/v1/terminal/command/',
    'user-auth': '/api/v1/users/auth/',
    'user-otp-auth': '/api/v1/users/otp/auth/',
    'user-assets': '/api/v1/perms/user/%s/assets/',
    'user-asset-groups': '/api/v1/perms/user/%s/nodes-assets/',
    'user-nodes-assets': '/api/v1/perms/user/%s/nodes-assets/',
    'my-profile': '/api/v1/users/profile/',
    'system-user-auth-info': '/api/v1/assets/system-user/%s/auth-info/',
    'validate-user-asset-permission': '/api/v1/perms/asset-permission/user/validate/',
    'finish-task': '/api/v1/terminal/tasks/%s/',
    'asset': '/api/v1/assets/assets/%s/',
    'system-user': '/api/v1/assets/system-user/%s',
    'user-profile': '/api/v1/users/profile/',
    'user-user': '/api/v1/users/users/%s/',
    'terminal-config': '/api/v1/terminal/terminal/config/',
    'token-asset': '/api/v1/users/connection-token/?token=%s',
    'domain-detail': '/api/v1/assets/domain/%s/',
    'ftp-log-list': '/api/v1/audits/ftp-log/',
    'org-list': '/api/v1/orgs/',
}
