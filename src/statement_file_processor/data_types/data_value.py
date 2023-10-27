"Data Value Model"
from typing import List, Callable, Union
from statement_file_processor.data_types.base_type import BaseType
from statement_file_processor.data_types.amount_value import AmountValue
from statement_file_processor.data_types.card_number_value import CardNumberValue
from statement_file_processor.data_types.date_value import DateValue
from statement_file_processor.data_types.description_value import DescriptionValue

DataValueType = Union[AmountValue, DateValue, DescriptionValue, CardNumberValue]

class DataValue(BaseType):
    "Data Value Model"

    def __init__(self):
        super().__init__()
        self.value: Callable[[DataValueType], DataValue]
        self.line: Callable[[int], DataValue]
        self.get_value:  Callable[[], DataValueType]
        self.get_line:  Callable[[], int]

    def get_fields(self) -> List[str]:
        return [
            "value",
            "line"
        ]
