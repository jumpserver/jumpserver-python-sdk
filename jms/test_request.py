# -*- coding: utf-8 -*-
#

import json
import unittest
from unittest import mock

from jms.request import HttpRequest, Http
from jms.exception import ResponseError


class TestHttpRequest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://www.jumpserver.org'
        self.method = "post"
        self.data = {"data": 123}
        self.data_json = json.dumps(self.data)
        self.param = {"hello": "world"}
        self.headers = {"Cookie": "123"}
        self.request = HttpRequest(self.url, method=self.method, data=self.data,
                                   params=self.param, headers=self.headers)

    def test_init(self):
        self.assertEqual(self.request.url, self.url)
        self.assertEqual(self.request.method, self.method)
        self.assertEqual(self.data, self.data)

    @mock.patch.object(HttpRequest, "methods")
    def test_do(self, mock_methods):
        mock_post = mock.MagicMock()
        mock_methods.get.return_value = mock_post
        self.request.do()
        self.assertTrue(mock_post.called)
        mock_post.assert_called_once_with(url=self.url, headers=self.request.headers, data=self.data_json, params=self.param)


class TestHttp(unittest.TestCase):
    def setUp(self):
        self.endpoint = "http://www.jumpserver.org"
        self.http = Http(self.endpoint)

    def test_clean_result_gte_500(self):
        resp_mock = mock.MagicMock()
        resp_mock.status_code = 500

        with self.assertRaises(ResponseError):
            self.http.clean_result(resp_mock)

    def test_clean_result_decode_error(self):
        resp_mock = mock.MagicMock()
        resp_mock.status_code = 200
        resp_mock.json.side_effect = json.JSONDecodeError("error", "\n\n", 1)

        with self.assertRaises(ResponseError):
            self.http.clean_result(resp_mock)

    def test_clean_result_ok(self):
        resp_mock = mock.MagicMock()
        resp_mock.status_code = 200

        self.assertEqual(self.http.clean_result(resp_mock), resp_mock)


if __name__ == '__main__':
    unittest.main()