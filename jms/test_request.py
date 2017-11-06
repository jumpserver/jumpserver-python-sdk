# -*- coding: utf-8 -*-
#

import json
import unittest
from unittest import mock
from unittest.mock import patch

from jms.request import HttpRequest


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

    # Todo: mock test
    @mock.patch('jms.request.requests.post')
    def test_do(self, mock_post):
        pass


if __name__ == '__main__':
    unittest.main()