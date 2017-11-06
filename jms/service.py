# -*- coding: utf-8 -*-
#

import base64
import logging
import sys

import time

from .auth import AppAccessKey, AccessKeyAuth
from .request import Http
from .applications import ApplicationsMixin
from .perms import PermsMixin
from .users import UsersMixin
from .assets import AssetsMixin
from .audits import AuditsMixin


class Service(UsersMixin, ApplicationsMixin, PermsMixin, AssetsMixin, AuditsMixin):
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)


class AppService(Service):
    access_key_class = AppAccessKey

    def __init__(self, app):
        super().__init__(app.config['CORE_HOST'])
        self.app = app
        self.access_key = self.access_key_class(self.app)

    def initial(self):
        self.load_access_key()
        self.set_auth()
        self.valid_auth()

    def load_access_key(self):
        # Must be get access key if not register it
        self.access_key.load()
        if self.access_key is None:
            logging.info("No access key found, register it")
            self.register_and_save()

    def set_auth(self):
        self.http.auth = AccessKeyAuth(self.access_key)

    def valid_auth(self):
        delay = 1
        while delay < 300:
            if self.terminal_heartbeat():
                msg = "Access key is not valid or need admin " \
                      "accepted, waiting %d s" % delay
                logging.info(msg)
                delay += 3
                time.sleep(3)
            else:
                break
        if delay >= 300:
            logging.info("Start timeout")
            sys.exit()

    def register_and_save(self):
        self.register()
        self.save_access_key()

    def save_access_key(self):
        self.access_key.save_to_file()

