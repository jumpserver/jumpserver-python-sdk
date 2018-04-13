# -*- coding: utf-8 -*-
#

import unittest
from unittest.mock import Mock

from jms.terminal import TerminalMixin
from jms.exception import RegisterError, RequestError


class ApplicationMixinTestCase(unittest.TestCase):

    def setUp(self):
        self.service = TerminalMixin("http://locahost")

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

    def test_terminal_register_409(self):
        mock_post = Mock()
        resp_mock = Mock()
        resp_mock.status_code = 409
        mock_post.post.return_value = resp_mock
        self.service.http = mock_post

        with self.assertRaises(RegisterError):
            self.service.terminal_register("app")

    def test_terminal_register_other(self):
        mock_post = Mock()
        resp_mock = Mock()
        resp_mock.status_code = 500
        resp_mock.json.return_value = {"msg": "error"}
        mock_post.post.return_value = resp_mock
        self.service.http = mock_post

        with self.assertRaises(RegisterError):
            self.service.terminal_register("app")

    def test_terminal_heartbeat_exception(self):
        mock = Mock()
        mock.post.side_effect = RequestError("Error")
        self.service.http = mock

        self.assertFalse(self.service.terminal_heartbeat())

    def test_terminal_heartbeat_failed(self):
        mock_post = Mock()
        resp_mock = Mock()
        resp_mock.status_code = 500
        mock_post.post.return_value = resp_mock
        self.service.http = mock_post

        self.assertFalse(self.service.terminal_heartbeat())

    def test_terminal_heartbeat_ok(self):
        mock_post = Mock()
        resp_mock = Mock()
        resp_mock.status_code = 201
        mock_post.post.return_value = resp_mock
        self.service.http = mock_post

        self.assertTrue(self.service.terminal_heartbeat())


if __name__ == "__main__":
    unittest.main()
