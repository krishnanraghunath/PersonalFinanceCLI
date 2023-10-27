'''Date Values model'''
from typing import Callable, List
from statement_file_processor.data_types.base_type import BaseType
from statement_file_processor.data_types.data_value import DataValue


class DataValues(BaseType):
    '''Date Values model'''

    def __init__(self) -> None:
        super().__init__()
        self.values: Callable[[List[DataValue]], DataValues]
        self.count: Callable[[int], DataValues]
        self.get_values:  Callable[[], List[DataValue]]
        self.get_count:  Callable[[], int]

    def add_value(self, value: DataValue) -> None:
        '''Add a given Data Value to list'''
        self.get_values().append(value)
        self.count(self.get_count() + 1)

    def get_fields(self) -> List[str]:
        return [
            "values",
            "count"
        ]
