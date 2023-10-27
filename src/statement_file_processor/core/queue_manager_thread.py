'''This would be observing each queue and create/kill processors accordingly'''
from __future__ import annotations
from queue import Queue
import logging
import threading
from typing import Optional, Callable, List
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.core.queue_consumer_thread import QueueConsumerThread


class QueueManagerThread(threading.Thread):
    '''This would be observing each queue and create/kill processors accordingly'''

    def __init__(self):
        super().__init__()
        self._monitoring_queue: Optional[Queue[QueueItem]] = None
        self._consumer_create_function: Optional[Callable[[],
                                                          Optional[QueueConsumerThread]]] = None
        self._threads: List[QueueConsumerThread] = []
        self._manage: threading.Event = threading.Event()
        self._maximum_workers: int = 10
        self._monitoring_interval: int = 1
        self._item_per_worker: int = 5
        self._current_active_workers: int = 0

    def with_maximum_workers(self, worker_count: int) -> QueueManagerThread:
        '''Set the maximum number of workers'''
        self._maximum_workers = worker_count
        return self

    def with_throughput(self, throughput: int) -> QueueManagerThread:
        '''Set the maximum queue length per worker'''
        self._item_per_worker = throughput
        return self

    def with_monitoring_interval(self, interval: int) -> QueueManagerThread:
        '''Set the monitoring interval'''
        self._monitoring_interval = interval
        return self

    def turn_on_monitoring(self) -> None:
        '''Turn on the monitoring'''
        self._manage.clear()
        if not self.is_alive():
            self.start()

    def turn_off_monitoring(self) -> None:
        '''Turn off the monitoring'''
        self._manage.set()
        for _thread in self._threads:
            _thread.request_stop()

    def wait_untill_done(self) -> None:
        '''Wait untill all the threads are joined'''
        self.turn_off_monitoring()
        for _thread in self._threads:
            _thread.join()

    def with_monitoring_queue(self, monitoring_queue: Queue[QueueItem]) -> QueueManagerThread:
        '''Set the monitoring queue for the manager'''
        self._monitoring_queue = monitoring_queue
        return self

    def get_consumer_create(self) -> Optional[Callable[[], Optional[QueueConsumerThread]]]:
        '''Return the consumer create function'''
        return self._consumer_create_function

    def consumer_create_function(self,
                                 consumer_create: Callable[[], QueueConsumerThread]) -> QueueManagerThread:
        '''Set the consumer create function'''
        self._consumer_create_function = consumer_create
        return self

    def _get_active_workers(self) -> int:
        return len(list(filter(lambda x: x.is_killed() is False, self._threads)))

    def set_limit(self, active_worker_count: int = 0):
        '''Add active worker based on limit required'''
        if active_worker_count == self._get_active_workers():
            return
        logging.info("Current workers: %d Required workers %d",\
                    self._get_active_workers(), active_worker_count)

        # If we dont have enough consumer object to fulfill, create them
        if active_worker_count > self._get_active_workers():
            for _ in range(0, active_worker_count - self._current_active_workers):
                # Create and add the newly created consumer to pool
                _consumer_thread_create_function = self.get_consumer_create()
                if _consumer_thread_create_function is not None:
                    _consumer_thread = _consumer_thread_create_function()
                    if _consumer_thread:
                        _consumer_thread.start()
                        self._threads.append(_consumer_thread)
                        logging.info("Added extra worker %s:%d",\
                                      _consumer_thread.get_group_name(),_consumer_thread.get_id())
                    else:
                        logging.error("Failed to create  consumer thread.")
                else:
                    logging.error("Consumer thread create function is not defined")
            return
        # First pass to disable any extra threads
        _extra_workers = self._get_active_workers() - active_worker_count
        for _consumer_thread in self._threads:
            if _extra_workers > 0:
                if not _consumer_thread.is_killed():
                    logging.info("Shutting down consumer %s:%s" ,\
                                  _consumer_thread.get_group_name(),_consumer_thread.get_id())
                    _consumer_thread.force_kill()
                    _extra_workers = _extra_workers - 1
        if _extra_workers > 0:
            logging.error(" Unable to reduce active worker count")

    def monitor(self):
        '''Create/Destroy threads based on dynamic requirement'''
        if not self._monitoring_queue:
            logging.error("Monitoring queue is not set!")
            return
        _qlen = self._monitoring_queue.qsize()
        if _qlen == 0:
            self.set_limit(0)
        else:
            self.set_limit(min(self._maximum_workers,
                               int(_qlen/self._item_per_worker) + 1))

    def run(self) -> None:
        while not self._manage.wait(self._monitoring_interval):
            self.monitor()
            if self._manage.is_set():
                return
