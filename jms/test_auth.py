# -*- coding: utf-8 -*-
#

import unittest
import os
import tempfile

from jms.auth import AccessKey, AccessKeyAuth, TokenAuth, SessionAuth
from jms.exceptions import LoadAccessKeyError


class MockRequest:
    def __init__(self):
        self.headers = {}


class TestAccessKeyAuth(unittest.TestCase):

    def setUp(self):
        self.access_key = AccessKey(id="123123123", secret="1231231231")
        self.req = MockRequest()

    def test_sign_request(self):
        auth = AccessKeyAuth(self.access_key)
        auth.sign_request(self.req)
        self.assertNotEqual(self.req.headers.get('Date', ''), '')
        self.assertIn(self.access_key.id, self.req.headers['Authorization'])
        self.assertIn('Sign', self.req.headers['Authorization'])
        print(self.req.headers)

    def tearDown(self):
        del self.req
        del self.access_key


class TestTokenAuth(unittest.TestCase):

    def setUp(self):
        self.token = "123123"
        self.req = MockRequest()

    def test_sign_request(self):
        auth = TokenAuth(self.token)
        auth.sign_request(self.req)
        self.assertEqual(self.req.headers['Authorization'], 'Bearer {}'.format(self.token))

        print(self.req.headers)


class TestSessionAuth(unittest.TestCase):
    def setUp(self):
        self.session_id = "123123"
        self.csrf_token = "123askdfj"
        self.req = MockRequest()

    def test_sign_request(self):
        auth = SessionAuth(self.session_id, self.csrf_token)
        auth.sign_request(self.req)
        self.assertEqual(
            self.req.headers['Cookie'],
            'sessionid={};csrftoken={}'.format(
                self.session_id, self.csrf_token
            )
        )
        self.assertEqual(self.req.headers['X-CSRFTOKEN'], self.csrf_token)
        print(self.req.headers)


class TestAccessKey(unittest.TestCase):
    def setUp(self):
        self.access_key_val = "123:123"
        self.id = "123"
        self.secret = "123"
        self.access_key = AccessKey("123", "123")

    def test_clean(self):
        with self.assertRaises(LoadAccessKeyError):
            AccessKey.clean("123123")
        self.assertEqual(AccessKey.clean(self.access_key_val), (self.id, self.secret))

    def test_load_from_val(self):
        with self.assertRaises(LoadAccessKeyError):
            AccessKey.load_from_val("2123")
        self.assertEqual(AccessKey.load_from_val(self.access_key_val), self.access_key)

    def test_load_from_env(self):
        env_var = "XX_ACCESS_KEY"
        os.environ[env_var] = self.access_key_val
        self.assertEqual(AccessKey.load_from_env(env_var), self.access_key)

    def test_load_from_f(self):
        with tempfile.NamedTemporaryFile('w+t') as f:
            f.write(self.access_key_val)
            f.flush()
            self.assertEqual(AccessKey.load_from_f(f.name), self.access_key)

    def test_save_to_f(self):
        tmpf = tempfile.mktemp()
        self.access_key.save_to_f(tmpf)
        print(tmpf)
        with open(tmpf, 'rt') as f:
            val = f.read().strip()
            self.assertEqual(val, self.access_key_val)
        os.unlink(tmpf)


if __name__ == '__main__':
    unittest.main()


