# -*- coding: utf-8 -*-
#
import logging

from .request import Http
from .exception import RequestError, ResponseError, RegisterError


class ApplicationsMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    def terminal_register(self, name):
        try:
            resp = self.http.post(
                'terminal-register', data={'name': name}, use_auth=False
            )
        except (RequestError, ResponseError) as e:
            logging.error(e)
            raise RegisterError(e)

        if resp.status_code == 201:
            access_key = resp.json()['access_key']
            access_key_id = access_key['id']
            access_key_secret = access_key['secret']
            return access_key_id, access_key_secret
        elif resp.status_code == 409:
            raise RegisterError('{} exist already'.format(name))
        else:
            msg = 'unknown: {}'.format(name, resp.json())
            raise RegisterError(msg)

    def terminal_heartbeat(self):
        """和Jumpserver维持心跳, 当Terminal断线后,jumpserver可以知晓

        Todo: Jumpserver发送的任务也随heatbeat返回, 并执行,如 断开某用户
        """
        try:
            resp = self.http.post('terminal-heartbeat', use_auth=True)
        except (ResponseError, RequestError):
            return False

        if resp.status_code == 201:
            return True
        else:
            return False
