# ~*~ coding: utf-8 ~*~

from jms import UserService


username = 'ibuler'
password = 'redhat'
endpoint = 'http://localhost:8080'

user_service = UserService(endpoint=endpoint)
data = {
    'username': username,
    'password': password,
    'public_key': None,
    'login_type': 'ST',
    'remote_addr': '2.2.2.2'
}
user, token = user_service.login(data)
print(user)
print(token)

user_service.auth(token=token)
print(user_service.is_authenticated())

print(user_service.get_my_assets())
print(user_service.get_my_asset_groups())


