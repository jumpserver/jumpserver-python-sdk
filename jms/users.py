# -*- coding: utf-8 -*-
#

from .exception import ResponseError, RequestError
from .models import User
from .request import Http

from .utils import get_logger

logger = get_logger(__file__)


class UsersMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    @property
    def role(self):
        user = self.get_profile()
        if user:
            return user.role
        else:
            return "Unknown"

    def authenticate_otp(self, seed, otp_code, login_type='T'):
        data = {
            'seed': seed,
            'otp_code': otp_code,
            'login_type': login_type,
        }

        try:
            resp = self.http.post('user-otp-auth', data=data, use_auth=False)
        except (ResponseError, RequestError):
            return False

        if resp.status_code == 200:
            return True
        else:
            return False

    def authenticate(self, username, password="", public_key="",
                     remote_addr="", login_type='T'):
        data = {
            'username': username,
            'password': password,
            'public_key': public_key,
            'remote_addr': remote_addr,
            'login_type': login_type,
        }
        try:
            resp = self.http.post('user-auth', data=data, use_auth=False)
        except (ResponseError, RequestError):
            return dict()

        if resp.status_code == 200:
            user = User.from_json(resp.json()["user"])
            token = resp.json()["token"]
            return {'user': user, 'token': token}
        elif resp.status_code == 300:
            user = User.from_json(resp.json()["user"])
            seed = resp.json()["seed"]
            return {'user': user, 'seed': seed}
        else:
            return dict()

    def check_user_cookie(self, session_id, csrf_token):
        try:
            headers = {"Cookie": "csrftoken={};sessionid={}".format(csrf_token, session_id)}
            resp = self.http.get('user-profile', headers=headers, use_auth=False)
        except (RequestError, ResponseError):
            return None
        return User.from_json(resp.json())

    def check_user_with_authorization(self, authorization):
        try:
            headers = {"Authorization": authorization}
            resp = self.http.get('user-profile', headers=headers, use_auth=False)
        except (ResponseError, ResponseError):
            return None
        return User.from_json(resp.json())

    def get_profile(self):
        try:
            resp = self.http.get('my-profile', use_auth=True)
        except (RequestError, ResponseError):
            return None

        if resp.status_code == 403:
            logger.error("Error code 403, permission deny, access key error")
        user = User.from_json(resp.json())
        return user

    def get_connection_token_info(self, token):
        try:
            params = {"token": token}
            resp = self.http.get('connection-token', params=params)
        except (ResponseError, RequestError):
            return {}
        return resp.json()

    def get_user_profile(self, user_id):
        try:
            resp = self.http.get('user-user', pk=user_id)
        except (RequestError, RequestError) as e:
            print("Get user profile failed: {}".format(e))
            return None
        if resp.status_code == 200:
            user = User.from_json(resp.json())
            return user
        else:
            print("Get user profile failed: {}".format(resp.content.decode()))
            return None

    def create_service_account(self, name, bootstrap_token):
        data = {"name": name}
        headers = {'Authorization': "BootstrapToken {}".format(bootstrap_token)}
        try:
            resp = self.http.post('service-account-list', data=data,
                                  use_auth=False, headers=headers)
        except (ResponseError, RequestError) as e:
            print("Service account create failed 1: {}".format(e))
            return None
        if resp.status_code == 201:
            user = User.from_json(resp.json())
            return user
        else:
            print("Service account create failed 2: {}".format(resp.content.decode()))
            return None

