# ~*~ coding: utf-8 ~*~

from jms import AppService

access_key_id = '600f6241-5574-407f-b39a-c616fb2b14eb'
access_key_secret = '48496c51-08fd-4eca-8c47-68b18aad72e9'

app_service = AppService(app_name='coco', endpoint='http://localhost:8080')
app_service.auth(access_key_id=access_key_id, access_key_secret=access_key_secret)

print(app_service.is_authenticated())
print(app_service.terminal_heatbeat())

system_user = {'id': 10, 'username': 'guang'}
print(app_service.get_system_user_auth_info(system_user))

data = {u'command_length': 0,
        u'date_finished': None,
        u'date_start': u'2012-12-12T12:12:11+08:00',
        u'hostname': u'test',
        u'id': 1,
        u'ip': u'192.168.1.2',
        u'is_finished': False,
        u'log_file': None,
        u'login_type': u'ST',
        u'name': u'admin',
        u'system_user': u'web',
        u'terminal': u'luna',
        u'time': u'',
        u'username': u'admin',
        u'was_failed': False}

app_service.send_proxy_log(data)

