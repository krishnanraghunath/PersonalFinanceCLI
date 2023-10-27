from optparse import OptionParser
from time import sleep 
from pathlib import Path
from pdfminer.high_level import extract_text
#from queue import Queue
# from multiprocessing import 

from multiprocessing import Manager

import sys
from typing import Any, Container, Optional, cast
import logging

from statement_file_processor.processors.statement_processors.hdfc_cc_statement_processor import HDFCCCStatementProcessor




# Setup the logging
fmt = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt,"%H:%M:%S"))
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)
logger.addHandler(handler)

sys.path.append(str(Path(__file__).parent)+'/')

from statement_file_processor.core.queue_consumer_thread import QueueConsumerThread
from statement_file_processor.core.queue_manager_thread import QueueManagerThread
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.queue_consumers.queue_consumer_file_extractors import QueueConsumerFileExtractors
from statement_file_processor.processors.statement_processors.icici_cc_statement_processor\
      import ICICICCStatementProcessor
from statement_file_processor.processors.statement_processors.kotak_cc_statement_processor\
      import KotakCCStatementProcessor
from statement_file_processor.queue_consumers.queue_consumer_distributor import QueueConsumerDistributor
from statement_file_processor.queue_consumers.queue_consumer_statement_processor import QueueConsumerStatementProcessor
from statement_file_processor.core.queue_consumer_process import QueueConsumerProcess 
from statement_file_processor.core.queue_manager_process import QueueManagerProcess


def pdf_file_extract_consumer_create() -> QueueConsumerProcess:
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

def icici_statement_processing_processor() -> QueueConsumerProcess:
    '''Create a file processing distributor processor'''
    _queue_consumer_distributor =cast(QueueConsumerStatementProcessor,\
            QueueConsumerStatementProcessor().\
            with_input_queue(icici_queue).\
            with_output_queue(processing_complete_queue).\
            with_error_queue(processing_error_queue)).\
            with_statement_processor(ICICICCStatementProcessor).\
            group("ICICIStatementExtractor")
    return _queue_consumer_distributor

if __name__ == '__main__':
# Queue List
  
    file_processing_queue = Manager().Queue()
    content_processing_router_queue  = Manager().Queue()
    processing_error_queue  = Manager().Queue()
    processing_complete_queue  = Manager().Queue()
    icici_queue  = Manager().Queue()


    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory",
                    help="Source directory for statements (mandatory)")
    (options, args) = parser.parse_args()
    if options.directory is None:
        print("Use python run.py --help")
        sys.exit(0)







    import time
    s = time.time()
    outfile = Path(__file__).parent/'out1.csv'
    icici = ICICICCStatementProcessor()
    icici.load_config('icici.json')
    for file_path in list(Path(options.directory).rglob("*.pdf"))[:None]:
        content = extract_text(file_path)
        proc = HDFCCCStatementProcessor()
        proc.load_config('hdfc.json')
        queue_item = QueueItem()
        queue_item.set_file_content(content)
        a,b,c = proc.process(queue_item)

        print(a)
        print(b)

        if a:
            file_path.unlink()
        try:
            outfile.write_text(content)
        except:
            print("FAIL")
            pass
        
    e = time.time()
    print("Time Taken = %d" % (e - s))
    sys.exit(0)

    s = time.time()
    qm_file_processor = QueueManagerProcess()\
                        .with_monitoring_queue(file_processing_queue)\
                        .consumer_create_function(pdf_file_extract_consumer_create)
    distributor = pdf_file_processing_distributor()
    qm_icici_processor = QueueManagerProcess()\
                        .with_monitoring_queue(icici_queue)\
                        .consumer_create_function(icici_statement_processing_processor)
    qm_icici_processor.turn_on_monitoring()
    distributor.start()
    qm_file_processor.turn_on_monitoring()


    tFiles = 0
    for file_path in Path(options.directory).rglob("*"):
        tFiles = tFiles + 1
        file_processing_queue.put(
            QueueItem().file_path(file_path))
    print("Total Files = %d" % tFiles)
    sleep(1)
    qm_file_processor.wait_untill_done()
    distributor.request_stop()
    qm_icici_processor.wait_untill_done()
    e = time.time()
    
    print("Time Taken = %d" % (e - s))

    print("File In Queue: %d" % file_processing_queue.qsize())
    print("File Out Queue: %d" % content_processing_router_queue.qsize())
    print("ICICI Queue: %d" % icici_queue.qsize())
    print("Pass Queue: %d" % processing_complete_queue.qsize())
    print("Fail Queue: %d" % processing_error_queue.qsize())

    print("Errors")
    while processing_error_queue.qsize() > 0:
        request_item = cast(QueueItem,processing_error_queue.get())
        
        print("###### %s ######" % request_item.get_input_file().name)
        for log in request_item.get_processing_history():
            print(log.get_log())
        print("###############\n\n")
        processing_error_queue.task_done()
    '''
    print("Results")
    while processing_complete_queue.qsize() > 0:
        request_item = processing_complete_queue.get()
        last_item_details = request_item.get_processing_history()[-1].get_item_details()
        if last_item_details:
            print(last_item_details.get_account_number())
            for t in last_item_details.get_transactions():
                print(t)
                '''