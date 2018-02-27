#! coding: utf-8

import datetime


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
                    v = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
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
    port = 22
    system_users_granted = []
    is_active = False
    system_users_join = ''
    comment = ""
    platform = "Linux"
    _system_users_name_list = None

    @classmethod
    def from_json(cls, json_dict):
        try:
            system_users_granted = SystemUser.from_multi_json(json_dict["system_users_granted"])
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

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.username


class AssetGroup(Decoder):
    id = 0
    name = ""
    assets_amount = 0
    comment = ""
    assets_granted = []

    @classmethod
    def from_json(cls, json_dict):
        assets_granted = Asset.from_multi_json(json_dict["assets_granted"])
        json_dict["assets_granted"] = assets_granted
        return super().from_json(json_dict)


class TerminalTask(Decoder):
    id = ""
    name = ""
    args = ""
    is_finished = False
