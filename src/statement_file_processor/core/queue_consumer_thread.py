'''The base class for reading and processing data from queue as a part of thread'''
from __future__ import annotations
import threading
from abc import ABC, abstractmethod
from typing import Optional
from queue import Empty, Queue
import logging
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.model.queue_processing_details import QueueProcessingDetails


class QueueConsumerThread(threading.Thread, ABC):
    '''The base class for reading and processing data from queue as a part of thread'''
    def __init__(self) -> None:
        super().__init__()
        self._input_queue: Optional[Queue[QueueItem]] = None
        self._output_queue: Optional[Queue[QueueItem]] = None
        self._dead_letter_queue: Optional[Queue[QueueItem]] = None
        # Continue flag is for looping for requests even if queue is empty
        self._continue = True
        # Active flag is for the entire loop. Will exit the loop if set to False
        self._active = True
        self._thread_group_id: Optional[str] = None
        self._id: int = id(self)

    def group(self, group_name: str) -> QueueConsumerThread:
        '''Returns a group id of the consumer. it is basically to identify
        threads doing same jobs'''
        self._thread_group_id = group_name
        return self

    def get_id(self) -> int:
        '''Return the thread id'''
        return self._id

    def get_group_name(self) -> Optional[str]:
        '''Return the group name of the thread'''
        return self._thread_group_id
    
    def get_input_queue(self) -> Optional[Queue[QueueItem]]:
        '''Returns the input queue'''
        return self._input_queue

    def with_input_queue(self, queue_in: Queue[QueueItem]) -> QueueConsumerThread:
        '''Set the input queue'''
        self._input_queue = queue_in
        return self

    def set_outout_queue(self, queue_out: Queue[QueueItem]) -> None:
        '''Set the output queue'''
        self._output_queue = queue_out

    def with_output_queue(self, queue_out: Queue[QueueItem]) -> QueueConsumerThread:
        '''Set the output queue'''
        if self._output_queue is None:
            self._output_queue = queue_out
        return self

    def with_error_queue(self, queue_error: Queue[QueueItem]) -> QueueConsumerThread:
        '''Set the error queue'''
        if self._dead_letter_queue is None:
            self._dead_letter_queue = queue_error
        return self

    def _fetch_item_from_queue(self) -> Optional[QueueItem]:
        '''Fetch the latest item from the queue and returns if it is the expected
        type'''
        try:
            input_queue = self.get_input_queue()
            # We would have already checked that the queue is not none
            # refconfirming it here once more and ofc for the
            # type checking (i am a novice in resolving type checking!!)
            if input_queue is not None:
                return input_queue.get_nowait()
        except Empty:
            pass
        return None

    def request_stop(self) -> None:
        '''Requesting the thread to stop once items are empty in the queue'''
        logging.info("Requesting Stop Consumer => %s:%s" , self.get_group_name(),self.get_id())
        self._continue = False

    def force_kill(self) -> None:
        '''Forcing the run process to stop from the next iteration of 
        fetching the item from queue'''
        logging.info("Killing Consumer => %s:%s" , self.get_group_name(),self.get_id())
        self._active = False

    def is_killed(self) -> bool:
        '''See if the thread was killed'''
        return self._active is False

    def run(self) -> None:
        logging.info("Starting Consumer => %s:%s" , self.get_group_name(),self.get_id())
        if self._input_queue is None or self._output_queue is None or\
                self._dead_letter_queue is None:
            print("Queues are not setup properly!!")
            return
        while (self._input_queue.qsize() > 0 or self._continue) and self._active:
            _request_item = self._fetch_item_from_queue()
            if _request_item is not None:
                processing_details = self.process(_request_item)
                if processing_details.is_processed():
                    # If the processing is succesful push the item to output queue
                    logging.info("%s:%s -> Pushing to Output Queue", self.get_group_name(), self.get_id())
                    self._output_queue.put(
                        _request_item.audit(processing_details))
                else:
                    logging.info("%s:%s -> Pushing to Error Queue", self.get_group_name(), self.get_id())
                    self._dead_letter_queue.put(
                        _request_item.audit(processing_details))
        logging.info("Stopping Consumer => %s:%s" , self.get_group_name(),self.get_id())

    @abstractmethod
    def process(self, request_item: QueueItem) -> QueueProcessingDetails:
        '''Process the return the processing details'''
