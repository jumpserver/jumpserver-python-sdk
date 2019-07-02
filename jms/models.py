#! coding: utf-8

import os
import datetime
import random
from hashlib import md5
import re

from .utils import ssh_key_string_to_obj, get_logger

logger = get_logger(__file__)


class Decoder:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    @classmethod
    def from_json(cls, json_dict):
        self = cls()
        for k, v in json_dict.items():
            if isinstance(getattr(self, k, None), datetime.datetime) and v:
                try:
                    if len(v.strip().split()) == 2:
                        v += " +0000"
                    v = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S %z")
                except TypeError:
                    pass
            if hasattr(self, k):
                setattr(self, k, v)
        return self

    @classmethod
    def from_multi_json(cls, json_dict_list):
        return [cls.from_json(json_dict) for json_dict in json_dict_list]


class User(Decoder):
    id = 0
    username = ""
    name = ""
    email = ""
    is_active = False
    is_superuser = False
    role = "User"
    groups = []
    wechat = ""
    phone = ""
    comment = ""
    access_key = ""
    date_expired = datetime.datetime.now()

    def __bool__(self):
        return self.id != 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Asset(Decoder):
    id = 0
    hostname = ""
    ip = ""
    protocol = ""
    port = 22
    protocols = []
    system_users_granted = []
    is_active = False
    system_users_join = ''
    comment = ""
    platform = "Linux"
    domain = ""
    org_id = ""
    org_name = ""
    _system_users_name_list = None

    @classmethod
    def from_json(cls, json_dict):
        try:
            system_users_granted = SystemUser.from_multi_json(
                json_dict.get("system_users_granted") or []
            )
            json_dict["system_users_granted"] = system_users_granted
        except KeyError:
            pass
        return super().from_json(json_dict)

    @property
    def system_users_name_list(self):
        """
        重写system_users_join，因为coco这里显示的是优先级最高的system_user
        :return:
        """
        if self._system_users_name_list:
            return self._system_users_name_list
        return '[' + ', '.join([s.name for s in self.system_users_granted]) + ']'

    @property
    def protocols_name(self):
        names = []
        for protocol in self.protocols:
            _name, port = protocol.split('/')
            names.append(_name)
        return names

    def has_protocol(self, name):
        return name in self.protocols_name

    def get_port_by_name(self, name):
        for protocol in self.protocols:
            _name, port = protocol.split('/')
            if _name.lower() == name:
                return port
        return None

    @property
    def ssh_port(self):
        port = self.get_port_by_name('ssh')
        if port is None:
            port = 22
        return port

    @property
    def telnet_port(self):
        port = self.get_port_by_name('telnet')
        if port is None:
            port = 23
        return port

    def __str__(self):
        return self.hostname

    def __repr__(self):
        return self.hostname


class SystemUser(Decoder):
    id = 0
    name = ""
    username = ""
    protocol = "ssh"
    auth_method = "P"
    comment = ""
    password = ""
    priority = 0
    private_key = None
    login_mode = ""
    actions = []

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.username


class AssetGroup(Decoder):
    id = 0
    name = ""
    key = ""
    assets_amount = 0
    comment = ""
    assets_granted = []

    @classmethod
    def from_json(cls, json_dict):
        assets_granted = Asset.from_multi_json(json_dict["assets_granted"])
        json_dict["assets_granted"] = assets_granted
        return super().from_json(json_dict)

    def __str__(self):
        return self.name


class TerminalTask(Decoder):
    id = ""
    name = ""
    args = ""
    is_finished = False

    def __str__(self):
        return self.name


class Gateway(Decoder):
    id = ""
    name = ""
    ip = ""
    port = 0
    protocol = ""
    username = ""
    is_active = True
    password = ""
    private_key = ""
    key_dir = None

    def __str__(self):
        return self.name

    def set_key_dir(self, key_dir):
        self.key_dir = key_dir

    @property
    def private_key_obj(self):
        if self.private_key and self.private_key.find('PRIVATE KEY'):
            key_obj = ssh_key_string_to_obj(self.private_key, self.password)
        else:
            key_obj = None
        return key_obj

    @property
    def private_key_file(self):
        if not self.key_dir:
            self.key_dir = '.'

        if not self.private_key:
            return None
        key_name = '.' + md5(self.private_key.encode('utf-8')).hexdigest()
        key_path = os.path.join(self.key_dir, key_name)
        if not os.path.exists(key_path):
            with open(key_path, 'w') as f:
                f.write(self.private_key)
            os.chmod(key_path, 0o400)
        return key_path


class Domain(Decoder):
    id = ""
    name = ""
    gateways = None

    @classmethod
    def from_json(cls, json_dict):
        data = super().from_json(json_dict)
        gateways = Gateway.from_multi_json(json_dict["gateways"])
        data.gateways = gateways
        return data

    def has_ssh_gateway(self):
        return bool([g for g in self.gateways if g.protocol == 'ssh'])

    def random_ssh_gateway(self):
        return random.choice([g for g in self.gateways if g.protocol == 'ssh'])

    def __str__(self):
        return self.name


class Org(Decoder):
    id = ""
    name = ""

    def __str__(self):
        return self.name


class CommandFilterRule(Decoder):
    type = {}
    priority = 100
    content = ""
    action = {}
    __pattern = None

    DENY, ALLOW, UNKNOWN, ERROR = range(4)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def _pattern(self):
        if self.__pattern:
            return self.__pattern
        if self.type['value'] == 'command':
            regex = []
            content = self.content.replace('\r\n', '\n')
            for cmd in content.split('\n'):
                cmd = cmd.replace(' ', '\s+')
                regex.append(r'\b{0}\b'.format(cmd))
            self.__pattern = re.compile(r'{}'.format('|'.join(regex)))
        else:
            self.__pattern = re.compile(r'{0}'.format(self.content))
        return self.__pattern

    def match(self, data):
        try:
            found = self._pattern.search(data)
        except Exception as e:
            logger.error(e)
            return self.ERROR, ''

        if not found:
            return self.UNKNOWN, ''

        if self.action['value'] == self.ALLOW:
            return self.ALLOW, found.group()
        elif self.action['value'] == self.DENY:
            return self.DENY, found.group()
        else:
            return False, ''


class AccessKey(Decoder):
    id = ""
    secret = ""


class ServiceAccount(Decoder):
    name = ""
    access_key = None

    @classmethod
    def from_json(cls, json_dict):
        data = super().from_json(json_dict)
        access_key = AccessKey.from_json(json_dict.get("access_key", {}))
        data.access_key = access_key
        return data


class Terminal(Decoder):
    id = ""
    name = ""
    remote_addr = ""
    comment = ""


class TerminalRegistration(Terminal):
    service_account = None

    @classmethod
    def from_json(cls, json_dict):
        data = super().from_json(json_dict)
        service_account = ServiceAccount.from_json(json_dict.get("service_account", {}))
        data.service_account = service_account
        return data
