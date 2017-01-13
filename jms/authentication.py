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


class SessionAuth(object):
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


class Auth(object):
    def __init__(self, token=None, access_key_id=None, access_key_secret=None,
                 session_id=None, csrf_token=None):

        if token is not None:
            self.instance = AccessTokenAuth(token)
        elif access_key_id and access_key_secret:
            self.instance = AccessKeyAuth(access_key_id, access_key_secret)
        elif session_id and csrf_token:
            self.instance = SessionAuth(session_id, csrf_token)
        else:
            raise OSError('Need token or access_key_id, access_key_secret'
                          'or session_id, csrf_token')

    def sign_request(self, req):
        return self.instance.sign_request(req)
