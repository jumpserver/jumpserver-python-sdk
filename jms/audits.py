# -*- coding: utf-8 -*-
#
import base64

from .request import Http
from .utils import timestamp_to_datetime_str


class AuditsMixin:
    def __init__(self, endpoint, auth=None):
        self.endpoint = endpoint
        self.auth = auth
        self.http = Http(endpoint, auth=self.auth)

    def send_proxy_log(self, data):
        """
        :param data: 格式如下
        data = {
            "user": "username",
            "asset": "name",
            "system_user": "web",
            "login_type": "ST",
            "was_failed": 0,
            "date_start": timestamp,
        }
        """
        assert isinstance(data.get('date_start'), (int, float))
        data['date_start'] = timestamp_to_datetime_str(data['date_start'])
        data['is_failed'] = 1 if data.get('is_failed') else 0

        r, content = self.http.post('send-proxy-log', data=data, use_auth=True)
        if r.status_code != 201:
            logging.warning('Send proxy log failed: %s' % content)
            return None
        else:
            return content['id']

    def finish_proxy_log(self, data):
        """ 退出登录资产后, 需要汇报结束 时间等

        :param data: 格式如下
        data = {
            "proxy_log_id": 123123,
            "date_finished": timestamp,
        }
        """
        assert isinstance(data.get('date_finished'), (int, float))
        data['date_finished'] = timestamp_to_datetime_str(data['date_finished'])
        data['is_failed'] = 1 if data.get('is_failed') else 0
        data['is_finished'] = 1
        proxy_log_id = data.get('proxy_log_id') or 0
        r, content = self.http.patch('finish-proxy-log', pk=proxy_log_id,
                                     data=data)

        if r.status_code != 200:
            logging.warning('Finish proxy log failed: %s' % proxy_log_id)
            return False
        return True

    def send_command_log(self, data):
        """用户输入命令后发送到Jumpserver保存审计
        :param data: 格式如下
        data = [{
            "proxy_log_id": 22,
            "user": "admin",
            "asset": "localhost",
            "system_user": "web",
            "command_no": 1,
            "command": "ls",
            "output": cmd_output, ## base64.b64encode(output),
            "timestamp": timestamp,
        },..]
        """
        assert isinstance(data, (dict, list))
        if isinstance(data, dict):
            data = [data]

        for d in data:
            if not d.get('output'):
                continue
            output = d['output'].encode('utf-8', 'ignore')
            d['output'] = base64.b64encode(output).decode("utf-8")

        result, content = self.http.post('send-command-log', data=data)
        if result.status_code != 201:
            logging.warning('Send command log failed: %s' % content)
            return False
        return True

    def send_record_log(self, data):
        """将输入输出发送给Jumpserver, 用来录像回放
        :param data: 格式如下
        data = [{
            "proxy_log_id": 22,
            "output": "backend server output, either input or output",
            "timestamp": timestamp,
        }, ...]
        """
        assert isinstance(data, (dict, list))
        if isinstance(data, dict):
            data = [data]
        for d in data:
            if d.get('output') and isinstance(d['output'], str):
                d['output'] = d['output'].encode('utf-8')
            d['output'] = base64.b64encode(d['output'])
        result, content = self.http.post('send-record-log', data=data)
        if result.status_code != 201:
            logging.warning('Send record log failed: %s' % content)
            return False
        return True
