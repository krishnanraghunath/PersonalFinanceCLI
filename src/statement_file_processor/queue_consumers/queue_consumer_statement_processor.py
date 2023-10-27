'''Processing the statement'''
from __future__ import annotations
from typing import Optional, Type
import logging
from statement_file_processor.core.queue_consumer_process import QueueConsumerProcess
from statement_file_processor.processors.statement_processors.pdf_statement_processor\
    import PDFStatementProcessor
from statement_file_processor.model.item_details import ItemDetails
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.model.queue_processing_details import QueueProcessingDetails


ProcessorType = Optional[Type[PDFStatementProcessor]]


class QueueConsumerStatementProcessor(QueueConsumerProcess):
    '''Processing the statement'''

    def __init__(self) -> None:
        QueueConsumerProcess.__init__(self)
        self._statement_processor: ProcessorType = None

    def with_statement_processor(self, processor: ProcessorType) -> QueueConsumerStatementProcessor:
        '''Set the statement processor type'''
        self._statement_processor = processor
        return self

    def get_statement_processor(self) -> ProcessorType:
        '''Return the statement processor'''
        return self._statement_processor

    def process(self, request_item: QueueItem) -> QueueProcessingDetails:
        '''It will process the statement'''
        _queue_processing_details = QueueProcessingDetails(self)
        _queue_processing_details.start()
        try:
            _statement_processor = self.get_statement_processor()
            if _statement_processor is not None:
                statement_processor = _statement_processor()
                result, info, transactions = statement_processor.process(
                    request_item)
                if result:
                    _queue_processing_details.add_item_details(ItemDetails().
                                                               with_transactions(transactions).
                                                               with_account_number(info))
                    _queue_processing_details.processed()
                    _queue_processing_details.log("Processing Succesfull")
                    logging.debug("%s:%s Processed the statement of %s",
                                  self.get_group_name(), self.get_id(), request_item.get_input_file())
                else:
                    logging.error(
                        "%s:%s -> %s", self.get_group_name(), self.get_id(), info)
                    _queue_processing_details.log(info)
            else:
                _queue_processing_details.log(
                    "No processor found to process the statement")
        except TypeError as e:
            _queue_processing_details.log(str(e))
        except AttributeError as e:
            _queue_processing_details.log(str(e))

        _queue_processing_details.end()
        return _queue_processing_details
