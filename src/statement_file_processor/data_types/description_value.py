'''Description Value Model'''
from typing import List, Callable
from statement_file_processor.data_types.base_type import BaseType


class DescriptionValue(BaseType):
    '''Description Value Model'''

    def __init__(self):
        super().__init__()
        self.description: Callable[[str], DescriptionValue]
        self.get_description:  Callable[[], str]

    def get_fields(self) -> List[str]:
        return [
            "description"
        ]
