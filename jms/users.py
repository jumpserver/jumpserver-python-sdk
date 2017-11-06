# -*- coding: utf-8 -*-
#

from .exception import ResponseError, RequestError
from .models import User
from .request import Http


class UsersMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    @property
    def role(self):
        try:
            resp = self.http.get('my-profile')
        except (RequestError, ResponseError):
            return "Unknown"

        user = User.from_json(resp.json())
        return user.role

    def authenticate(self, username, password="", pubkey="",
                     remote_addr="8.8.8.8", login_type='ST'):
        data = {
            'username': username,
            'password': password,
            'public_key': pubkey,
            'remote_addr': remote_addr,
            'login_type': login_type,
        }
        try:
            resp = self.http.post('user-auth', data=data, use_auth=False)
        except (ResponseError, RequestError):
            return None

        if resp.status_code == 200:
            user = User.from_json(resp.json()["user"])
            return user
        else:
            return None

    def check_user_cookie(self, session_id, csrf_token):
        pass
