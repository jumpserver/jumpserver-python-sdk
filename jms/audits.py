# -*- coding: utf-8 -*-
#

from .exception import ResponseError, RequestError


class AuditsMixin:
    def create_ftp_log(self, data):
        """
        上传FTP日志
        :param data: {
                   "user": "",
                   "asset": ""<
                   "system_user": "",
                   "remote_addr": "",
                   "operate": "",
                   "filename": "",
                   "date_start": "",
                   "is_success": True or False
               }
        :return: True or False
        """

        try:
            resp = self.http.post('ftp-log-list', data=data, use_auth=True)
        except (RequestError, ResponseError):
            return None
        if resp.status_code == 201:
            return True
        else:
            return False

