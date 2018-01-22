# -*- coding: utf-8 -*-
#
import datetime
import sys
import time

from .exception import RegisterError
from .utils import get_logger
from .auth import AppAccessKey, AccessKeyAuth, TokenAuth
from .request import Http
from .terminal import TerminalMixin
from .perms import PermsMixin
from .users import UsersMixin
from .assets import AssetsMixin


logger = get_logger(__file__)


class Service(UsersMixin, TerminalMixin, PermsMixin, AssetsMixin):
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)


class AppService(Service):
    access_key_class = AppAccessKey
    auth_class = AccessKeyAuth

    def __init__(self, app):
        super().__init__(app.config['CORE_HOST'])
        self.app = app
        self.access_key = self.access_key_class(self.app)

    def initial(self):
        logger.debug("Initial app service")
        self.load_access_key()
        self.set_auth()
        self.valid_auth()
        logger.debug("Service http auth: {}".format(self.http.auth))

    def load_access_key(self):
        logger.debug("Load access key")
        self.access_key.load()
        if not self.access_key:
            logger.info("No access key found, register it")
            self.register_and_save()

    def set_auth(self):
        logger.debug("Set app service auth: {}".format(self.access_key))
        self.auth = self.auth_class(self.access_key)
        self.http.set_auth(self.auth_class(self.access_key))

    def valid_auth(self):
        delay = 1
        while delay < 10:
            user = self.get_profile()
            if not user:
                msg = "Connect server error or access key is invalid, " \
                      "remove `./keys/.access_key` run again"
                logger.error(msg)
                delay += 3
                time.sleep(3)
            else:
                break
        if delay >= 10:
            sys.exit()

    def wait_for_accept(self, uuid, token):
        delay = 1
        while delay < 3600:
            try:
                self.access_key.id, self.access_key.secret = self.retrieve_access_key(
                    uuid, token,
                )
                break
            except RegisterError as e:
                logger.info(e)
                delay += 3
                time.sleep(3)
                continue

    def register_and_save(self):
        try:
            uuid, token = self.terminal_register(self.app.name)
        except RegisterError as e:
            logger.error("Failed register terminal %s" % e)
            sys.exit()

        self.wait_for_accept(uuid, token)
        if not self.access_key:
            logger.error("Register error")
            sys.exit()
        self.save_access_key()

    def save_access_key(self):
        self.access_key.save_to_file()


class UserService(Service):

    def __init__(self, endpoint):
        super().__init__(endpoint)
        self.username = ""
        self.password = ""
        self.pubkey = ""

    def refresh_token(self):
        if self.username:
            self.login(self.username, self.password, self.pubkey)
        else:
            logger.info("You need login first")

    def login(self, username, password=None, pubkey=None):
        user, token = self.authenticate(username, password=password, public_key=pubkey)
        if user.is_active and user.date_expired > datetime.datetime.now():
            self.auth = TokenAuth(token=token)
        self.username = username
        self.password = password
        self.pubkey = pubkey
        return user



