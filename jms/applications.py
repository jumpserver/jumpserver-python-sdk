# -*- coding: utf-8 -*-
#
import logging

import os
import psutil

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

    def terminal_heartbeat(self, sessions):
        """和Jumpserver维持心跳, 当Terminal断线后,jumpserver可以知晓

        :return tasks that this terminal need handle

        push data as:

        data = {
            "cpu_used": 1.0,
            "memory_used": 12332,
            "connections": 12,
            "threads": 123,
            "boot_time": 123232323.0,
            "sessions": [{}, {}],
            "session_online": 10
        }
        """
        p = psutil.Process(os.getpid())
        data = {
            "cpu_used": p.cpu_percent(interval=1.0),
            "memory_used": p.memory_info().rss,
            "connections": len(p.connections()),
            "threads": p.num_threads(),
            "boot_time": p.create_time(),
            "session_online": len([s for s in sessions if not s["is_finished"]]),
            "sessions": sessions,
        }
        print(sessions)
        try:
            resp = self.http.post('terminal-heartbeat', data=data, use_auth=True)
        except (ResponseError, RequestError):
            return False

        if resp.status_code == 201:
            return []
        else:
            return []
