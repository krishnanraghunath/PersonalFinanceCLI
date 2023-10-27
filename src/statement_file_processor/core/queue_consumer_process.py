'''The base class for reading and processing data from queue as a part of thread'''
from __future__ import annotations
import multiprocessing
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from queue import Empty, Queue
import logging
from time import time

if TYPE_CHECKING:
    from statement_file_processor.model.queue_item import QueueItem
    from statement_file_processor.model.queue_processing_details import QueueProcessingDetails

class QueueConsumerProcess(multiprocessing.Process, ABC):
    '''The base class for reading and processing data from queue as a part of thread'''
    def __init__(self) -> None:
        super().__init__()
        self._input_queue: Optional[Queue[QueueItem]] = None
        self._output_queue: Optional[Queue[QueueItem]] = None
        self._dead_letter_queue: Optional[Queue[QueueItem]] = None
        self._thread_group_id: Optional[str] = None
        self._id: int = id(self)

    def group(self, group_name: str) -> QueueConsumerProcess:
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

    def with_input_queue(self, queue_in: Queue[QueueItem]) -> QueueConsumerProcess:
        '''Set the input queue'''
        self._input_queue = queue_in
        return self

    def set_outout_queue(self, queue_out: Queue[QueueItem]) -> None:
        '''Set the output queue'''
        self._output_queue = queue_out

    def with_output_queue(self, queue_out: Queue[QueueItem]) -> QueueConsumerProcess:
        '''Set the output queue'''
        if self._output_queue is None:
            self._output_queue = queue_out
        return self

    def with_error_queue(self, queue_error: Queue[QueueItem]) -> QueueConsumerProcess:
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

    def run(self) -> None:
        logging.info("Starting Consumer Process => %s:%s" , self.get_group_name(),self.get_id())
        if self._input_queue is None or self._output_queue is None or\
                self._dead_letter_queue is None:
            print("Queues are not setup properly!!")
            return
        time_s = time()
        # Making the consumer alive for sometime
        while self._input_queue.qsize() > 0 or (time() - time_s) < 10:
            _request_item = self._fetch_item_from_queue()
            if _request_item is not None:
                logging.info("%s" , _request_item.get_input_file())
                processing_details = self.process(_request_item)
                if processing_details.is_processed():
                    # If the processing is succesful push the item to output queue
                    logging.debug("%s:%s -> Pushing to Output Queue", self.get_group_name(), self.get_id())
                    self._output_queue.put(
                        _request_item.audit(processing_details))
                else:
                    logging.debug("%s:%s -> Pushing to Error Queue", self.get_group_name(), self.get_id())
                    self._dead_letter_queue.put(
                        _request_item.audit(processing_details))
        logging.info("Stopping Consumer Process => %s:%s" , self.get_group_name(),self.get_id())

    @abstractmethod
    def process(self, request_item: QueueItem) -> QueueProcessingDetails:
        '''Process the return the processing details'''
