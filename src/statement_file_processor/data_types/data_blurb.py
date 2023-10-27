'''Data Blurb Model'''
from typing import List, Callable
from statement_file_processor.data_types.base_type import BaseType


class DataBlurb(BaseType):
    '''Data Blurb Model'''

    def __init__(self) -> None:
        super().__init__()
        self.start_line: Callable[[int], DataBlurb]
        self.end_line: Callable[[int], DataBlurb]
        self.get_start_line: Callable[[], int]
        self.get_end_line: Callable[[], int]


    def get_fields(self) -> List[str]:
        return [
            "start_line",
            "end_line"
        ]
