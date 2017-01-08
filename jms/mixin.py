# ~*~ coding: utf-8 ~*~

import os
import logging
import time
import threading
import six

from .exceptions import LoadAccessKeyError


class AppMixin(object):
    def __init__(self):
        self.user_service = None
        self.app_service = None
        self.config = None

    def load_access_key_from_env(self, env=None, delimiter=':'):
        if env is None and self.config.get('ACCESS_KEY_ENV'):
            env = self.config.get('ACCESS_KEY_ENV')
        if env and isinstance(env, six.string_types):
            try:
                access_key = os.environ.get(env).split(delimiter)
                if len(access_key) == 2:
                    return access_key
            except AttributeError:
                pass
        raise LoadAccessKeyError

    def load_access_key_from_config(self, delimiter=':'):
        if self.config and self.config.get('ACCESS_KEY'):
            access_key = self.config.get('ACCESS_KEY').split(delimiter)
            if len(access_key) == 2:
                return access_key
        raise LoadAccessKeyError

    def load_access_key_from_f(self, f=None, delimiter=':'):
        access_key = None
        if f is None and self.config.get('ACCESS_KEY_STORE', None):
            f = self.config.get('ACCESS_KEY_STORE')

        if isinstance(f, six.string_types) and os.path.isfile(f):
            f = open(f)
        else:
            raise LoadAccessKeyError

        if isinstance(f, file):
            for line in f:
                if line and not line.strip().startswith('#'):
                    try:
                        access_key = line.strip().split(delimiter)
                        break
                    except ValueError:
                        pass
            f.close()

        if len(access_key) == 2:
            return access_key

        raise LoadAccessKeyError

    def load_access_key(self, **kwargs):
        """Should return access_key_id, access_key_secret"""
        access_key = None
        for method in [self.load_access_key_from_config,
                       self.load_access_key_from_f,
                       self.load_access_key_from_env]:
            try:
                access_key = method(**kwargs)
            except LoadAccessKeyError:
                continue
        return access_key

    def save_access_key_to_f(self, access_key_id, access_key_secret, access_key_store=None):
        if access_key_store is None and self.config.get('ACCESS_KEY_STORE'):
            access_key_store = self.config.get('ACCESS_KEY_STORE')

        if access_key_store is None:
            raise IOError('No valid access key store')

        if isinstance(access_key_store, six.string_types):
            access_key_store = open(access_key_store, 'w')

        if isinstance(access_key_store, file):
            access_key_store.write('{0}:{1}'.format(access_key_id, access_key_secret))
            access_key_store.close()
        else:
            raise IOError('No valid access key store')

    def register(self, access_key_store=None):
        is_success, content = self.app_service.terminal_register()
        if is_success:
            access_key_id = content.access_key_id
            access_key_secret = content.access_key_secret
            logging.warning('Your can save access_key: (%s:%s) somewhere or set it in config'
                            % (access_key_id, access_key_secret))
            self.save_access_key_to_f(access_key_id, access_key_secret, access_key_store)
            return access_key_id, access_key_secret
        else:
            logging.warning(content.msg)
            return None

    def app_auth(self):
        access_key = self.load_access_key()
        if access_key is None or None in access_key:
            access_key = self.register()
        if access_key and len(access_key) == 2:
            logging.info('Using access key id: %s' % access_key[0])
            self.app_service.auth(*access_key)


    def heatbeat(self):
        def _keep():
            while True:
                result = self.app_service.terminal_heatbeat()
                if not result:
                    logging.warning('Terminal heatbeat failed or Terminal need accepted')
                time.sleep(self.config['HEATBEAT_INTERVAL'])

        thread = threading.Thread(target=_keep, args=())
        thread.daemon = True
        thread.start()

