'''Details regarding the processing status of a queue item to be returned from the queue consumer'''
from __future__ import annotations
from time import time
from typing import List, Optional, TYPE_CHECKING, Union
from statement_file_processor.core.queue_consumer_process import QueueConsumerProcess
from statement_file_processor.model.item_details import ItemDetails
if TYPE_CHECKING:
    from core.queue_consumer_thread import QueueConsumerThread


class QueueProcessingDetails:
    '''Details regarding the processing status of a queue item to be returned from the queue consumer'''

    def __init__(self, queue_consumer: Union[ QueueConsumerThread, QueueConsumerProcess]) -> None:
        self._time: int = 0
        self._start_time: int = 0
        self._end_time: int = 0
        self._processed: bool = False
        self._consumer_id: int = queue_consumer.get_id()
        self._consumer_group: Optional[str] = queue_consumer.get_group_name()
        self._logs: List[str] = []
        self._item_details: Optional[ItemDetails] = None

    def is_processed(self) -> bool:
        '''Return is the last item has been processed succesfully'''
        return self._processed

    def start(self) -> None:
        '''Start the processing'''
        self._start_time = int(time()*1000)

    def end(self) -> None:
        '''End the processing'''
        self._end_time = int(time()*1000)
        self._time = self._end_time - self._start_time

    def processed(self) -> None:
        '''Processing has been done succesfully'''
        self._processed = True

    def log(self, log: str) -> None:
        '''Add the log'''
        self._logs.append(log)

    def add_item_details(self, item_details: ItemDetails) -> None:
        '''Add item details post succesfull processing'''
        self._item_details = item_details
    
    def get_item_details(self) -> Optional[ItemDetails]:
        '''Return the item details'''
        return self._item_details

    def get_consumer_group(self) -> str:
        '''Return the consumer group'''
        if self._consumer_group:
            return self._consumer_group
        return "UNKNOWN"

    def get_log(self) -> List[str]:
        '''Return logs'''
        return self._logs