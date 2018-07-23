# Jumpserver SDK

为 Jumpserver ssh terminal 和 web terminal封装了一个sdk, 完成和Jumpserver
交互的一些功能


- Service
通用RestApi 接口类

- AppService
增加了app注册等

- UserService
用户使用该类

    

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

    
