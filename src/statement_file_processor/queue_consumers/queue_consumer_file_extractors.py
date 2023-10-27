'''Consume the request item and load the file content into the request item'''
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from statement_file_processor.core.queue_consumer_process import QueueConsumerProcess
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.model.queue_processing_details import QueueProcessingDetails


class QueueConsumerFileExtractors(QueueConsumerProcess):
    '''Consume the request item and load the file content into the request item'''

    def __init__(self) -> None:
        QueueConsumerProcess.__init__(self)
        self.group("PDFFileExtractor")

    def process(self, request_item: QueueItem) -> QueueProcessingDetails:
        _queue_processing_details = QueueProcessingDetails(self)
        _queue_processing_details.start()
        try:
            file_name = request_item.get_input_file()
            if file_name is not None:
                _pdf_text_data = extract_text(file_name)
                request_item.set_file_content(_pdf_text_data)
                _queue_processing_details.log("File Extraction:Succesfull")
                _queue_processing_details.processed()
            else:
                _queue_processing_details.log("File Path is None for request")
        except FileNotFoundError as e:
            _queue_processing_details.log(str(e))
        except PDFSyntaxError as e:
            _queue_processing_details.log(str(e))
        finally:
            _queue_processing_details.end()
        return _queue_processing_details
