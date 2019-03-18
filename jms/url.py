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
    'user-otp-auth': '/api/users/v1/otp/auth/',
    'user-assets': '/api/perms/v1/user/%s/assets/',
    'user-asset-groups': '/api/perms/v1/user/%s/nodes-assets/',
    'user-nodes-assets': '/api/perms/v1/user/%s/nodes-assets/',
    'my-profile': '/api/users/v1/profile/',
    'system-user-auth-info': '/api/assets/v1/system-user/%s/auth-info/',
    'system-user-asset-auth-info': '/api/assets/v1/system-user/%s/asset/%s/auth-info/',
    'validate-user-asset-permission': '/api/perms/v1/asset-permission/user/validate/',
    'finish-task': '/api/terminal/v1/tasks/%s/',
    'asset': '/api/assets/v1/assets/%s/',
    'asset-list': '/api/assets/v1/assets/',
    'system-user': '/api/assets/v1/system-user/%s',
    'user-profile': '/api/users/v1/profile/',
    'user-user': '/api/users/v1/users/%s/',
    'terminal-config': '/api/terminal/v1/terminal/config/',
    'token-asset': '/api/users/v1/connection-token/?token=%s',
    'domain-detail': '/api/assets/v1/domain/%s/',
    'ftp-log-list': '/api/audits/v1/ftp-log/',
    'org-list': '/api/orgs/v1/orgs/',
    'system-user-cmd-filter-rule-list': '/api/assets/v1/system-user/%s/cmd-filter-rules/',
    'terminal-registration': '/api/terminal/v2/terminal-registrations/',
}
