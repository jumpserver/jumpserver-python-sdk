# Jumpserver SDK

为 Jumpserver ssh terminal 和 web terminal封装了一个sdk, 完成和Jumpserver
交互的一些功能


### App service
这是为terminal app 提供的 class

- \__init__(self, app_name=None, endpoint=None)

    app_name: app的名称
    endpoint: Jumpserver api的地址

- auth(self, access_key_id=None, access_key_secret=None)
    对app进行认证, 以后请求jumpserver api会使用这个access key
    
    access_key_id: 认证使用的id
    access_key_secret: 认证使用的secret
    
- check_auth(self)
    检查用户access key是否合法, True or False

- terminal_heatbeat()
    和Jumpserver保持心跳, True or False

- get_system_user_auth_info(self, system_user)
    返回系统用户的密码和密钥
    system_user = {
        "id": 系统用户id,
        "username": 系统用户的用户名,
        "name": 系统用户的名称
    }
- send_proxy_log(self, data)
    用户登陆资产,向Jumpserver发送登录信息
    data = {
        "username": 用户名,
        "name": 用户姓名,
        "hostname": 登陆资产的hostname,
        "ip": 登录资产的ip地址,
        "system_user": 系统用户用户名,
        "login_type": 登录方式['ST', 'WT'] ST: SSHTerminal, WT: WebTerminal
        "was_failed": 是否成功登陆, 0或1
        "date_start": 一个时间日期对象, 开始时间
    }
        
    返回成功的信息, 带有id

- finish_proxy_log(self, data)
    用户登出, 向Jumpserver发送登出信息
    data = {
        "date_finished": 一个时间日期对象, 登出的时间,
        "proxy_log_id": 上个send_proxy_log取到的id,
    }
        
    
```
In [1]: from jms import AppService

In [2]: access_key_id = '600f6241-5574-407f-b39a-c616fb2b14eb'

In [3]: access_key_secret = '48496c51-08fd-4eca-8c47-68b18aad72e9'

In [4]: app_service = AppService(app_name='coco', endpoint='http://localhost:8080')

In [5]: app_service.auth(access_key_id=access_key_id, access_key_secret=access_key_secret)

In [6]: app_service.check_auth()
Out[6]: True

In [7]: app_service.terminal_heatbeat()
Out[7]: True

In [9]: system_user = {'id': 10, 'username': 'guang'}

In [10]: app_service.get_system_user_auth_info(system_user)
Out[10]: (u'sagittis', None)
                 
In [14]: app_service.send_proxy_log(data)
Out[14]:
DotMap([(u'username', u'admin'),
        (u'date_start', u'2012-12-12T12:12:11+08:00'),
        (u'system_user', u'web'),
        (u'name', u'admin'),
        (u'date_finished', None),
        (u'ip', u'192.168.1.2'),
        (u'hostname', u'test'),
        (u'command_length', 0),
        (u'terminal', u'luna'),
        (u'time', u''),
        (u'was_failed', False),
        (u'login_type', u'ST'),
        (u'is_finished', False),
        (u'log_file', None),
        (u'id', 7)])

```


### User service
User service封装了用户调用的api, 如用户登录,获取授权的资产等

- login(self, username=None, password=None,
        public_key=None, login_type='', remote_addr=''):
      用户登录api
      返回
        ({'username': 'test', ...}, 'token': 'Token String')
            
      username: 用户名
      password: 密码
      public_key: 公钥
      login_type: ['ST', 'WT'] SSHTerminal, WebTerminal
      remote_addr: 用户的ip
      
- auth(self, token=None)
     使用token签名请求, 用户请求api都需要使用签名, login例外
     
- is_authenticated(self):
     判断认证是否有效, 返回 True或False
     
- get_my_assets(self)
    返回该用户有权限的资产
    [{'hostname': '192.168.1.1', 'ip': '192.168.1.1', ...}, {}]
 
- get_my_asset_groups(self)
    返回该用户后权限的资产组, 这个资产组并非是直接授权资产组, 而是取出所有资产,
    再取出每个资产所有的资产组,去重
    [{'name': 'group1', 'comment': 'something'}, ... ]
    
- get_user_asset_group_assets(self, asset_group_id)
    返回该用户授权这个资产组下的资产,并非所有该资产组下的资产,而是被授权的资产
    [{'hostname': '192.168.1.1', 'ip': '192.168.1.1', ...}, {}]
    
    
```
In [1]: from jms import UserService

In [2]: username = 'ibuler'

In [3]: password = 'redhat'

In [4]: user_service = UserService(app_name='coco', endpoint='http://localhost:8080')

In [5]: user, token = user_service.login(username=username, password=password, 
                public_key=None, login_type='ST', remote_addr='2.2.2.2')
                
                
Out[10]: user
DotMap([(u'username', u'ibuler'),
        (u'comment', u''),
        (u'name', u'\u5e7f\u5b8f\u4f1f'),
        (u'date_expired', u'2086-12-21 16:00:00'),
        (u'is_superuser', False),
        (u'is_active', True),
        (u'email', u'ibuler@qq.com'),
        (u'phone', u''),
        (u'wechat', u''),
        (u'groups', [u'asdfasdf']),
        (u'role', u'User'),
        (u'id', 99)])

In [11]: token
Out[11]: u'c47a9b0da67c47f3885efa92b6a3de28'

In [17]: user_service.is_authenticated()
Out[17]: True

In [18]: user_service.get_my_assets()
Out[18]:
[DotMap([(u'comment', u''),
         (u'system_users_join', u'marilyn, sarah, gloria'),
         (u'ip', u'48.48.48.48'),
         (u'hostname', u'carolyn81'),
         (u'is_active', True),
         (u'port', 22),
         (u'system_users', ...

]

In [19]: user_service.get_my_asset_groups()
Out[19]:
[DotMap([(u'comment', u'In sagittis dui vel nisl.'),
         (u'id', 51),
         (u'name', u'Paula Berry'),
         (u'assets_amount', 1)]),
 DotMap([(u'comment', u'Mauris ullamcorper purus sit amet nulla.'),
         (u'id', 67),
         (u'name', u'Amanda Dunn'),
         (u'assets_amount', 1)]), ...
 ]
 
In [20]: user_service.get_user_asset_group_assets(51)
Out[20]:
[DotMap([(u'comment', u''),
         (u'system_users_join', u'jennifer, melissa, nancy, rebecca'),
         (u'ip', u'1.1.1.1'),
         (u'hostname', u'heather89'),
         (u'is_active', True),
         (u'port', 22),
         (u'system_users',
          [DotMap([(u'username', u'jennifer'),
                   (u'comment', u'Aenean sit amet justo.'),
                   (u'shell', u'/bin/bash'),
                   (u'protocol', u'ssh'),
                   (u'name', u'Angela Henry'),
                   (u'auto_update', True),
                   (u'sudo', u'/user/bin/whoami'),..
]
```

    
