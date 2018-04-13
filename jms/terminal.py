# -*- coding: utf-8 -*-
#

import os
import psutil

from .utils import get_logger
from .request import Http
from .models import TerminalTask
from .exception import RequestError, ResponseError, RegisterError

logger = get_logger(__file__)


class TerminalMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    def retrieve_access_key(self, uuid, token):
        try:
            params = {"token": token}
            resp = self.http.get('terminal-access-key', pk=uuid, params=params, use_auth=False)
        except (ResponseError, RequestError) as e:
            logger.error(e)
            raise RegisterError(e)

        if resp.status_code in (400, 401):
            raise RegisterError(resp.text)
        access_key = resp.json()["access_key"]
        access_key_id = access_key['id']
        access_key_secret = access_key['secret']
        return access_key_id, access_key_secret

    def terminal_register(self, name):
        try:
            resp = self.http.post(
                'terminal-register', data={'name': name}, use_auth=False
            )
        except (RequestError, ResponseError) as e:
            logger.error(e)
            raise RegisterError(e)

        if resp.status_code == 201:
            data = resp.json()
            uuid = data["id"]
            token = data["token"]
            return uuid, token
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
        try:
            resp = self.http.post('terminal-heartbeat', data=data, use_auth=True)
        except (ResponseError, RequestError) as e:
            logger.debug("Request auth: {}".format(self.http.auth))
            logger.error(e)
            return False

        if resp.status_code == 403:
            logger.debug("Auth failed")

        if resp.status_code == 201:
            return TerminalTask.from_multi_json(resp.json())
        else:
            return []

    def push_session_replay(self, gzip_file, session_id):
        with open(gzip_file, 'rb') as f:
            files = {"file": f}
            try:
                resp = self.http.post(
                    'session-replay', files=files,
                    content_type=None, pk=session_id
                )
            except (ResponseError, RequestError) as e:
                logger.error(e)
                return False

            if resp.status_code == 201:
                return True
            else:
                return False

    def get_session_replay(self, session_id):
        try:
            resp = self.http.get('session-replay', pk=session_id)
        except (RequestError, ResponseError) as e:
            logger.error(e)
            return None

        if resp.status_code == 200:
            return resp
        else:
            logger.error("Session replay response code not 200")
            return None

    def push_session_command(self, data_set):
        try:
            resp = self.http.post('session-command', data=data_set)
        except (RequestError, ResponseError) as e:
            logger.error(e)
            return False
        if resp.status_code == 201:
            return True
        else:
            return False

    def create_session(self, session_data):
        try:
            resp = self.http.post('session-list', data=session_data)
        except (RequestError, ResponseError) as e:
            logger.error(e)
            return None

        if resp.status_code == 201:
            return resp.json()
        else:
            return None

    def finish_session(self, session_data):
        try:
            session_id = session_data["id"]
            date_end = session_data["date_end"]
            data = {'is_finished': True, "date_end": date_end}
            resp = self.http.patch('session-detail', pk=session_id, data=data)
        except (ResponseError, RequestError) as e:
            logger.error(e)
            return None

        if resp.status_code == 200:
            return resp.json
        else:
            return None

    def finish_replay(self, session_id):
        try:
            data = {'has_replay': True}
            resp = self.http.patch('session-detail', pk=session_id, data=data)
        except (ResponseError, RequestError) as e:
            logger.error(e)
            return None

        if resp.status_code == 200:
            return True
        else:
            return False

    def finish_task(self, task_id):
        data = {"is_finished": True}
        try:
            resp = self.http.patch('finish-task', pk=task_id, data=data)
        except (RequestError, ResponseError) as e:
            logger.error(e)
            return False

        if resp.status_code == 200:
            return True
        else:
            return False

    def load_config_from_server(self):
        try:
            resp = self.http.get('terminal-config')
        except (RegisterError, ResponseError) as e:
            logger.error(e)
            return {}
        if resp.status_code == 200:
            configs = {}
            data = resp.json()
            for k, v in data.items():
                configs[k.replace('TERMINAL_', '')] = v
            return configs



