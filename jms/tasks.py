# ~*~ coding: utf-8 ~*~
import threading
import logging
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty


class QueueMultiMixin(object):
    def mget(self, size=1, block=True, timeout=5):
        items = []
        for i in range(size):
            try:
                items.append(self.get(block=block, timeout=timeout))
            except Empty:
                break
        return items


class MemoryQueue(Queue, QueueMultiMixin):
    pass


class Task(object):
    def __init__(self, queue, action, threads_num=4, batch_count=20, idle_time=4):
        self.queue = queue
        self.action = action
        self.threads_num = threads_num
        self.batch_count = batch_count
        self.idle_time = idle_time

    def handler(self):
        while True:
            data = self.queue.mget(size=self.batch_count)
            if data:
                logging.debug('Sending data: %s' % data)
                self.action(data)

    def run(self):
        threads = []
        for i in range(self.threads_num):
            t = threading.Thread(target=self.handler)
            threads.append(t)
            t.daemon = True
            t.start()


# class CommandTask(object):
#     size = 10
#
#     def handler(self):
#         while True:
#             data = command_queue.mget(size=self.size)
#             if data:
#                 service.send_command_log(data)
#
#     def run(self, threads_count=2):
#         threads = []
#         for i in range(threads_count):
#             t = threading.Thread(target=self.handler)
#             t.daemon = True
#             t.start()
#         for t in threads:
#             t.join()
#
#
# class RecordTask(object):
#     size = 10
#
#     def handler(self):
#         while True:
#             data = record_queue.mget(size=self.size)
#             if data:
#                 service.send_record_log(data)
#
#     def run(self, threads_count=2):
#         threads = []
#         for i in range(threads_count):
#             t = threading.Thread(target=self.handler)
#             t.daemon = True
#             t.start()
#         for t in threads:
#             t.join()