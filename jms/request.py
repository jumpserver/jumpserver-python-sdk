# -*- coding: utf-8 -*-
#
import os
import json
import simplejson

import requests
from requests.structures import CaseInsensitiveDict

from .exception import RequestError, ResponseError, RegisterError
from .url import API_URL_MAPPING

_USER_AGENT = 'jms-sdk-py'
CACHED_TTL = os.environ.get('CACHED_TTL', 30)


class HttpRequest(object):
    methods = {
        'get': requests.get,
        'post': requests.post,
        'patch': requests.patch,
        'put': requests.put,
        'delete': requests.delete,
    }

    def __init__(self, url, method='get', data=None, params=None,
                 headers=None, content_type='application/json', **kwargs):
        self.url = url
        self.method = method
        self.params = params or {}
        self.kwargs = kwargs

        if not isinstance(headers, dict):
            headers = {}
        self.headers = CaseInsensitiveDict(headers)
        if content_type:
            self.headers['Content-Type'] = content_type
        if data:
            self.data = json.dumps(data)
        else:
            self.data = {}

    def do(self):
        # logging.debug("{} {}: \n\tHeaders {}, \n\tData {}, \n\tParams {}, \n\tOther: {}".format(
        #     self.method.upper(), self.url, self.headers,
        #     self.data, self.params, self.kwargs
        # ))
        result = self.methods.get(self.method)(
            url=self.url, headers=self.headers,
            data=self.data, params=self.params,
            **self.kwargs
        )
        return result


class Http(object):

    def __init__(self, endpoint, auth=None):
        self.auth = auth
        self.endpoint = endpoint

    def set_auth(self, auth):
        self.auth = auth

    @staticmethod
    def clean_result(resp):
        if resp.status_code >= 500:
            raise ResponseError("Response code is {0.status_code}: {0.text}".format(resp))

        try:
            _ = resp.json()
        except (json.JSONDecodeError, simplejson.scanner.JSONDecodeError):
            raise ResponseError("Response json couldn't be decode: {0.text}".format(resp))
        else:
            return resp

    def do(self, api_name=None, pk=None, method='get', use_auth=True,
           data=None, params=None, content_type='application/json', **kwargs):

        if api_name in API_URL_MAPPING:
            path = API_URL_MAPPING.get(api_name)
            if pk and '%s' in path:
                path = path % pk
        else:
            path = '/'

        url = self.endpoint.rstrip('/') + path
        req = HttpRequest(url, method=method, data=data,
                          params=params, content_type=content_type,
                          **kwargs)
        if use_auth:
            if not self.auth:
                raise RequestError('Authentication required')
            else:
                self.auth.sign_request(req)

        try:
            resp = req.do()
        except (requests.ConnectionError, requests.ConnectTimeout) as e:
            raise RequestError("Connect endpoint {} error: {}".format(self.endpoint, e))

        return self.clean_result(resp)

    def get(self, *args, **kwargs):
        kwargs['method'] = 'get'
        return self.do(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs['method'] = 'post'
        return self.do(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs['method'] = 'put'
        return self.do(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs['method'] = 'patch'
        return self.do(*args, **kwargs)
