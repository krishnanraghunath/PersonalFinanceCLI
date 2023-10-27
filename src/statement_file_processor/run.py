from optparse import OptionParser
from time import sleep 
from pathlib import Path
from queue import Queue
import sys
from typing import cast
import logging 

# Setup the logging
fmt = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt,"%H:%M:%S"))
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.addHandler(handler)

sys.path.append(str(Path(__file__).parent.parent)+'/')

from core.queue_consumer_thread import QueueConsumerThread
from core.queue_manager_thread import QueueManagerThread
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.queue_consumers.queue_consumer_file_extractors import QueueConsumerFileExtractors
from statement_file_processor.processors.statement_processors.icici_cc_statement_processor\
      import ICICICCStatementProcessor
from statement_file_processor.queue_consumers.queue_consumer_distributor import QueueConsumerDistributor
from statement_file_processor.queue_consumers.queue_consumer_statement_processor import QueueConsumerStatementProcessor


# Queue List
file_processing_queue: Queue[QueueItem] = Queue()
content_processing_router_queue: Queue[QueueItem]  = Queue()
processing_error_queue: Queue[QueueItem]  = Queue()
processing_complete_queue: Queue[QueueItem]  = Queue()

#Seperate Queues for groups
icici_queue: Queue[QueueItem]  = Queue()



parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory",
                  help="Source directory for statements (mandatory)")
(options, args) = parser.parse_args()
if options.directory is None:
    print("Use python run.py --help")
    sys.exit(0)






from pdfminer.high_level import extract_text
import time
s = time.time()
for file_path in Path(options.directory).rglob("*"):
    content = extract_text(file_path)
    icici = ICICICCStatementProcessor()
    queue_item = QueueItem()
    queue_item.set_file_content(content)
    a,b,c = icici.process(queue_item)
e = time.time()
print("Time Taken = %d" % (e - s))


s = time.time()

for file_path in Path(options.directory).rglob("*"):
    file_processing_queue.put(
        QueueItem().file_path(file_path))

def pdf_file_extract_consumer_create() -> QueueConsumerThread:
    '''Create a new File Extractor consumer'''
    return (QueueConsumerFileExtractors()
                .with_input_queue(file_processing_queue)
                .with_output_queue(content_processing_router_queue)
                .with_error_queue(processing_error_queue))

def pdf_file_processing_distributor() -> QueueConsumerThread:
    '''Create a file processing distributor processor'''
    _queue_consumer_distributor =cast(QueueConsumerDistributor,
            QueueConsumerDistributor().\
            with_input_queue(content_processing_router_queue).\
            with_output_queue(icici_queue).\
            with_error_queue(processing_error_queue)).\
            with_group_queue_map("ICICI",icici_queue)
    return _queue_consumer_distributor

def icici_statement_processing_processor() -> QueueConsumerThread:
    '''Create a file processing distributor processor'''
    _queue_consumer_distributor =cast(QueueConsumerStatementProcessor,\
            QueueConsumerStatementProcessor().\
            with_input_queue(icici_queue).\
            with_output_queue(processing_complete_queue).\
            with_error_queue(processing_error_queue)).\
            with_statement_processor(ICICICCStatementProcessor).\
            group("ICICIStatementExtractor")
    return _queue_consumer_distributor

distributor = pdf_file_processing_distributor()
distributor.start()
qm_fileprocessing = QueueManagerThread()\
                        .with_monitoring_queue(file_processing_queue)\
                        .consumer_create_function(pdf_file_extract_consumer_create)

qm_icici_processor = QueueManagerThread()\
                        .with_monitoring_queue(icici_queue)\
                        .consumer_create_function(icici_statement_processing_processor)
qm_fileprocessing.turn_on_monitoring()
qm_icici_processor.turn_on_monitoring()
sleep(5)

#qm_fileprocessing.turn_off_monitoring()
qm_fileprocessing.wait_untill_done()
distributor.request_stop()
sleep(5)
qm_icici_processor.wait_untill_done()
distributor.force_kill()


e = time.time()
print("Time Taken = %d" % (e - s))
'''
print("Errors")
while processing_error_queue.qsize() > 0:
    request_item = processing_error_queue.get()
    for log in request_item.get_processing_history():
        print(log.get_log())
    processing_error_queue.task_done()

print("Results")
while processing_complete_queue.qsize() > 0:
    request_item = processing_complete_queue.get()
    last_item_details = request_item.get_processing_history()[-1].get_item_details()
    if last_item_details:
        print(last_item_details.get_account_number())
        for t in last_item_details.get_transactions():
            print(t)
            '''