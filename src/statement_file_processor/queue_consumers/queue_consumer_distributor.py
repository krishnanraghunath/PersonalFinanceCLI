'''Get the item from the file processed queue and put it into seperate queues'''
from __future__ import annotations
from queue import Queue
import logging
from typing import Dict
from statement_file_processor.core.queue_consumer_thread import QueueConsumerThread
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.model.queue_processing_details import QueueProcessingDetails


class QueueConsumerDistributor(QueueConsumerThread):
    '''Get the item from the file processed queue and put it into seperate queues'''

    def __init__(self) -> None:
        QueueConsumerThread.__init__(self)
        self.group(group_name="Queue Distributor")
        self._group_queue_map: Dict[str, Queue[QueueItem]] = {}

    def with_group_queue_map(self, group_name: str, group_queue: Queue[QueueItem])\
            -> QueueConsumerDistributor:
        '''Add group to queue map'''
        self._group_queue_map[group_name] = group_queue
        return self

    def process(self, request_item: QueueItem) -> QueueProcessingDetails:
        ''' It will move the message towards a queue which was not proceed it already'''
        _queue_processing_details = QueueProcessingDetails(self)
        _queue_processing_details.start()
        # Get all the queues which have processed the item
        failed_group_processors = [x.get_consumer_group()
                                   for x in request_item.get_processing_history()]
        for _group, _queue in self._group_queue_map.items():
            # If the specific group is not failed forward the message to the specific group
            if _group not in failed_group_processors:
                # Set the output queue so that message will be send to the queue
                logging.info("Forwading the message to %s",_group)
                self.set_outout_queue(_queue)
                _queue_processing_details.log(f"Forwarding to {_group}")
                _queue_processing_details.end()
                _queue_processing_details.processed()
                return _queue_processing_details
        # if there are no queues left. push to the error queue
        logging.error("All processor options have been\
                      tried. Can not be processed further")
        _queue_processing_details.log(
            "Failed to find any remaining queues to process")
        _queue_processing_details.end()
        return _queue_processing_details
