# -*- coding: utf-8 -*-
#

from .exception import ResponseError, RequestError
from .models import Org

from .utils import get_logger

logger = get_logger(__file__)


class OrgMixin:
    def get_orgs(self):
        try:
            resp = self.http.get('org-list')
        except (RequestError, ResponseError) as e:
            logger.warn(e)
            return []
        if resp.status_code == 200:
            orgs = Org.from_multi_json(resp.json())
            return orgs
        else:
            return []

