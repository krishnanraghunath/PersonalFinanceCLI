'''Card Number Value Model'''
from typing import Callable, List
from statement_file_processor.data_types.base_type import BaseType

class CardNumberValue(BaseType):
    '''Card Number Value Model'''

    def __init__(self) -> None:
        super().__init__()
        self.get_card_number: Callable[[], str]
        self.card_number: Callable[[str], CardNumberValue]

    def get_fields(self) -> List[str]:
        return [
            "card_number"
        ]
