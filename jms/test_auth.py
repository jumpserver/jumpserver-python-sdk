# -*- coding: utf-8 -*-
#

import unittest
import os
import tempfile
from copy import deepcopy

from jms.auth import AccessKey, AccessKeyAuth, TokenAuth, SessionAuth, \
    AppAccessKey
from jms.exception import LoadAccessKeyError


class MockRequest:
    def __init__(self):
        self.headers = {}


class MockApp:
    def __init__(self, config):
        self.config = config


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
        access_key = AccessKey()
        with self.assertRaises(LoadAccessKeyError):
            access_key.load_from_val("2123")
        access_key.load_from_val(self.access_key_val)
        self.assertEqual(access_key, self.access_key)

    def test_load_from_env(self):
        env_var = "XX_ACCESS_KEY"
        os.environ[env_var] = self.access_key_val
        access_key = AccessKey()
        access_key.load_from_env(env_var)
        self.assertEqual(access_key, self.access_key)

    def test_load_from_f(self):
        with tempfile.NamedTemporaryFile('w+t') as f:
            f.write(self.access_key_val)
            f.flush()
            access_key = AccessKey()
            access_key.load_from_f(f.name)
            self.assertEqual(access_key, self.access_key)

    def test_save_to_f(self):
        tmpf = tempfile.mktemp()
        self.access_key.save_to_f(tmpf)
        print(tmpf)
        with open(tmpf, 'rt') as f:
            val = f.read().strip()
            self.assertEqual(val, self.access_key_val)
        os.unlink(tmpf)


class TestAppAccessKey(unittest.TestCase):
    def setUp(self):
        self.access_key_val = "123:123"
        self.id = "123"
        self.secret = "123"
        self.access_key = AccessKey("123", "123")
        self.key_env_var = "XXX_ACCESS_KEY"
        self.key_file = tempfile.mktemp()
        config = {
            'ACCESS_KEY_ENV': self.key_env_var,
            'ACCESS_KEY': self.access_key_val,
            'ACCESS_KEY_FILE': self.key_file,
        }
        self.mock_app = MockApp(config)
        self.app_access_key = AppAccessKey(self.mock_app)

    def test_load_from_conf_env(self):
        os.environ[self.key_env_var] = self.access_key_val
        app_access_key = deepcopy(self.app_access_key)
        app_access_key.load_from_conf_env()
        self.assertEqual(app_access_key, self.access_key)

    def test_load_from_conf_val(self):
        app_access_key = deepcopy(self.app_access_key)
        app_access_key.load_from_conf_val()
        self.assertEqual(app_access_key, self.access_key)

    def test_load_from_conf_file(self):
        with open(self.key_file, 'wt') as f:
            f.write(self.access_key_val)
        app_access_key = deepcopy(self.app_access_key)
        app_access_key.load_from_conf_file()
        self.assertEqual(app_access_key, self.access_key)

    def test_load(self):
        with open(self.key_file, 'wt') as f:
            f.write(self.access_key_val)
        app_access_key = deepcopy(self.app_access_key)
        app_access_key.load()
        self.assertEqual(app_access_key, self.access_key)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()


