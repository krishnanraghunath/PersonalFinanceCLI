'''This would be observing each queue and create/kill processors accordingly'''
from __future__ import annotations
from queue import Queue
import logging
import threading
from typing import Optional, Callable, List
from statement_file_processor.core.queue_consumer_process import QueueConsumerProcess
from statement_file_processor.model.queue_item import QueueItem


class QueueManagerProcess(threading.Thread):
    '''This would be observing each queue and create/kill processors accordingly'''

    def __init__(self):
        super().__init__()
        self._monitoring_queue: Optional[Queue[QueueItem]] = None
        self._consumer_create_function: Optional[Callable[[],
                                                          Optional[QueueConsumerProcess]]] = None
        self._processes: List[QueueConsumerProcess] = []
        self._manage: threading.Event = threading.Event()
        self._maximum_workers: int = 10
        self._monitoring_interval: int = 1
        self._item_per_worker: int = 5
        self._current_active_workers: int = 0

    def with_maximum_workers(self, worker_count: int) -> QueueManagerProcess:
        '''Set the maximum number of workers'''
        self._maximum_workers = worker_count
        return self

    def with_throughput(self, throughput: int) -> QueueManagerProcess:
        '''Set the maximum queue length per worker'''
        self._item_per_worker = throughput
        return self

    def with_monitoring_interval(self, interval: int) -> QueueManagerProcess:
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

    def wait_untill_done(self) -> None:
        '''Wait untill all the threads are joined'''
        self.turn_off_monitoring()
        for _process in self._processes:
            _process.join()

    def with_monitoring_queue(self, monitoring_queue: Queue[QueueItem]) -> QueueManagerProcess:
        '''Set the monitoring queue for the manager'''
        self._monitoring_queue = monitoring_queue
        return self

    def get_consumer_create(self) -> Optional[Callable[[], Optional[QueueConsumerProcess]]]:
        '''Return the consumer create function'''
        return self._consumer_create_function

    def consumer_create_function(self,
                                 consumer_create: Callable[[], QueueConsumerProcess]) -> QueueManagerProcess:
        '''Set the consumer create function'''
        self._consumer_create_function = consumer_create
        return self

    def _get_active_workers(self) -> int:
        return len(list(filter(lambda x: x.is_alive(), self._processes)))

    def set_limit(self, active_worker_count: int = 0):
        '''Add active worker based on limit required'''
        if active_worker_count == self._get_active_workers():
            return
        logging.debug("Current workers: %d Required workers %d",\
                    self._get_active_workers(), active_worker_count)

        # If we dont have enough consumer object to fulfill, create them
        if active_worker_count > self._get_active_workers():
            for _ in range(0, active_worker_count - self._current_active_workers):
                # Create and add the newly created consumer to pool
                _consumer_process_create_function = self.get_consumer_create()
                if _consumer_process_create_function is not None:
                    _consumer_process = _consumer_process_create_function()
                    if _consumer_process:
                        _consumer_process.start()
                        self._processes.append(_consumer_process)
                        logging.debug("Added extra worker %s:%d",\
                                      _consumer_process.get_group_name(),_consumer_process.get_id())
                    else:
                        logging.error("Failed to create  consumer process.")
                else:
                    logging.error("Consumer process create function is not defined")
            return


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
