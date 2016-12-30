#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from . import utils


class AccessKeyAuth(object):
    def __init__(self, access_key_id, access_key_secret):
        self.id = access_key_id
        self.secret = access_key_secret

    def sign_request(self, req):
        req.headers['Date'] = utils.http_date()
        signature = utils.make_signature(self.secret)
        req.headers['Authorization'] = "Sign {0}:{1}".format(self.id, signature)
        return req


class AccessTokenAuth(object):
    def __init__(self, token):
        self.token = token

    def sign_request(self, req):
        req.headers['Authorization'] = 'Bearer {0}'.format(self.token)
        return req


class Auth(object):
    def __init__(self, token=None, access_key_id=None, access_key_secret=None):
        self.token = token
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

        if token is not None:
            self.instance = AccessTokenAuth(token)
        elif access_key_id and access_key_secret:
            self.instance = AccessKeyAuth(access_key_id, access_key_secret)
        else:
            raise OSError('Need token or access_key_id, access_key_secret')

    def sign_request(self, req):
        return self.instance.sign_request(req)
