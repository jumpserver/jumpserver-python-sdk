#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

URL_MAP = {
    'terminal-register': '/api/applications/v1/terminal/register/',
    'terminal-heatbeat': '/api/applications/v1/terminal/heatbeat/',
    'send-proxy-log': '/api/audits/v1/proxy-log/receive/',
    'finish-proxy-log': '/api/audits/v1/proxy-log/%s/',
    'proxy_log_finish': '/api/audits/v1/proxy-log/%s/',
    'command_log_create': '/api/audits/v1/command-log/',
    'user-auth': '/api/users/v1/auth/',
    'my-assets': '/api/perms/v1/user/my/assets/',
    'my-asset-groups': '/api/perms/v1/user/my/asset-groups/',
    'assets-of-group': '/api/perms/v1/user/my/asset-group/%s/assets/',
    'my-profile': '/api/users/v1/profile/',
    'system-user-auth-info': '/api/assets/v1/system-user/%s/auth-info/',
}
