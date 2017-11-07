# -*- coding: utf-8 -*-
#

import unittest
from unittest.mock import patch, Mock

from jms.applications import ApplicationsMixin
from jms.exception import RegisterError


class ApplicationMixinTestCase(unittest.TestCase):

    def setUp(self):
        self.service = ApplicationsMixin("http://locahost")

    def test_terminal_register_raise_exception(self):
        mock = Mock()
        mock.post.side_effect = RegisterError("Error")
        self.service.http = mock
        with self.assertRaises(RegisterError):
            self.service.terminal_register("hello")

    def test_terminal_register_201(self):
        mock_post = Mock()
        resp_mock = Mock()
        resp_mock.status_code = 201
        resp_mock.json.return_value = {"access_key": {"id": "123", "secret": "234"}}
        mock_post.post.return_value = resp_mock
        self.service.http = mock_post

        _id, _secret = self.service.terminal_register("app")
        mock_post.post.assert_called_once_with("terminal-register", data={"name": "app"}, use_auth=False)
        self.assertEqual(_id, "123")
        self.assertEqual(_secret, "234")


if __name__ == "__main__":
    unittest.main()
