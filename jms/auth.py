# -*- coding: utf-8 -*-
#

import os
import logging

from . import utils
from .exceptions import LoadAccessKeyError


class AccessKeyAuth:
    def __init__(self, access_key):
        self.access_key = access_key

    def sign_request(self, req):
        date = utils.http_date()
        req.headers['Date'] = date
        signature = utils.make_signature(self.access_key.secret, date=date)
        req.headers['Authorization'] = "Sign {0}:{1}".format(self.access_key.id, signature)
        return req


class TokenAuth:
    def __init__(self, token):
        self.token = token

    def sign_request(self, req):
        req.headers['Authorization'] = 'Bearer {0}'.format(self.token)
        return req


class SessionAuth:
    def __init__(self, session_id, csrf_token):
        self.session_id = session_id
        self.csrf_token = csrf_token

    def sign_request(self, req):
        cookie = [v for v in req.headers.get('Cookie', '').split(';')
                  if v.strip()]
        cookie.extend(['sessionid='+self.session_id,
                       'csrftoken='+self.csrf_token])
        req.headers['Cookie'] = ';'.join(cookie)
        req.headers['X-CSRFTOKEN'] = self.csrf_token
        return req


class PrivateTokenAuth:

    def __init__(self, token):
        self.token = token

    def sign_request(self, req):
        req.headers['Authorization'] = 'Token {0}'.format(self.token)
        return req


class AccessKey(object):
    def __init__(self, id=None, secret=None):
        self.id = id
        self.secret = secret

    @staticmethod
    def clean(value, sep=':', silent=False):
        try:
            id, secret = value.split(sep)
        except (AttributeError, ValueError) as e:
            if not silent:
                raise LoadAccessKeyError(e)
            return '', ''
        else:
            return id, secret

    @classmethod
    def load_from_val(cls, val, **kwargs):
        id, secret = cls.clean(val, **kwargs)
        return cls(id=id, secret=secret)

    @classmethod
    def load_from_env(cls, env, **kwargs):
        value = os.environ.get(env)
        id, secret = cls.clean(value, **kwargs)
        return cls(id=id, secret=secret)

    @classmethod
    def load_from_f(cls, f, **kwargs):
        value = ''
        if isinstance(f, str) and os.path.isfile(f):
            f = open(f)
        if hasattr(f, 'read'):
            for line in f:
                if line and not line.strip().startswith('#'):
                    value = line.strip()
                    break
            f.close()
        id, secret = cls.clean(value, **kwargs)
        return cls(id=id, secret=secret)

    def save_to_f(self, f, silent=False):
        if isinstance(f, str):
            f = open(f, 'wt')
        try:
            f.write('{0}:{1}'.format(self.id, self.secret))
        except IOError:
            if not silent:
                raise
        finally:
            f.close()

    def __bool__(self):
        return bool(self.id and self.secret)

    def __eq__(self, other):
        return self.id == other.id and self.secret == other.secret

    def __str__(self):
        return '{0}:{1}'.format(self.id, self.secret)

    def __repr__(self):
        return '{0}:{1}'.format(self.id, self.secret)


class AppAccessKey:
    """使用Access key来认证"""

    def __init__(self, app):
        self.app = app
        self.access_key = None

    @property
    def id(self):
        return self.access_key.id if self.access_key else ''

    @property
    def secret(self):
        return self.access_key.secret if self.access_key else ''

    @property
    def _key_env(self):
        return self.app.config['ACCESS_KEY_ENV']

    @property
    def _key_val(self):
        return self.app.config['ACCESS_KEY']

    @property
    def _key_file(self):
        return self.app.config['ACCESS_KEY_FILE']

    def load_from_conf_env(self, sep=':', silent=False):
        self.access_key = AccessKey.load_from_env(self._key_env, sep=sep, silent=silent)

    def load_from_conf_val(self, sep=':', silent=False):
        self.access_key = AccessKey.load_from_val(self._key_val, sep=sep, silent=silent)

    def load_from_conf_file(self, sep=':', silent=False):
        self.access_key = AccessKey.load_from_f(self._key_file, sep=sep, silent=silent)

    def load(self, **kwargs):
        """Should return access_key_id, access_key_secret"""
        for method in [self.load_from_conf_env,
                       self.load_from_conf_val,
                       self.load_from_conf_file]:
            try:
                return method(**kwargs)
            except LoadAccessKeyError:
                continue
        return None

    def save_to_file(self):
        return self.access_key.save_to_f(self._key_file)

    # def __getattr__(self, item):
    #     return getattr(self.access_key, item)
