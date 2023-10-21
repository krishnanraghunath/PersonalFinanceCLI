'''Card Number Value Model'''
from typing import List
from PersonalFinanceCLI.models.BaseModel import BaseModel


class CardNumberValue(BaseModel):
    '''Card Number Value Model'''

    def __init__(self) -> None:
        super().__init__()

    def get_fields(self) -> List[str]:
        return [
            "cardNumber"
        ]
