# ~*~ coding: utf-8 ~*~

import logging
import time
import threading

from .exceptions import LoadAccessKeyError


class AppMixin(object):
    service = None
    config = None

    def app_auth(self):
        try:
            self.service.auth_magic()
        except LoadAccessKeyError:
            is_success, content = self.service.register_terminal()
            if is_success:
                self.service.access_key.id = content.access_key_id
                self.service.access_key.secret = content.access_key_secret
                self.service.access_key.save_to_key_store()
                self.service.auth()
            else:
                raise SystemExit('Register terminal failed, may be'
                                 'have been exist, you should look for'
                                 'the terminal access key, set in config, '
                                 'or put it in access key store'
                                 )

    def heatbeat(self):
        def _keep():
            while True:
                result = self.service.terminal_heatbeat()
                if not result:
                    logging.warning('Terminal heatbeat failed or '
                                    'Terminal need accepted by administrator')
                time.sleep(self.config['HEATBEAT_INTERVAL'])

        thread = threading.Thread(target=_keep, args=())
        thread.daemon = True
        thread.start()

