'''Object representing the item in queue'''
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
from statement_file_processor.model.queue_processing_details import QueueProcessingDetails

class QueueItem:
    '''Object representing the item in queue'''

    def __init__(self) -> None:
        self._input_file: Optional[Path] = None
        self._file_content: Optional[str] = None
        self._processing_history: List[QueueProcessingDetails] = []

    def file_path(self, file_location: Path) -> QueueItem:
        '''Set the input file path'''
        self._input_file = file_location
        return self

    def audit(self, processing_log: QueueProcessingDetails) -> QueueItem:
        '''Add the audit log entry for the item'''
        self._processing_history.append(processing_log)
        return self

    def set_file_content(self, file_content: str) -> None:
        '''Set the content of the file'''
        self._file_content = file_content

    def get_input_file(self) -> Optional[Path]:
        '''Return the input file name'''
        return self._input_file

    def get_file_content(self) -> Optional[str]:
        '''Return the content of the fiel'''
        return self._file_content

    def get_processing_history(self) -> List[QueueProcessingDetails]:
        '''Return the queue processing history'''
        return self._processing_history
