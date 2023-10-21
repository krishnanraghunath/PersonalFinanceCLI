'''Data Model for TagRule Collection'''
from typing import Any, Callable, Dict, List, Optional, Type
from PersonalFinanceCLI.models.BaseModel import BaseModel
from PersonalFinanceCLI.models.transactions.DateValue import DateValue


class TagRuleModel(BaseModel):
    '''Data Model for TagRule Collection'''

    def __init__(self) -> None:
        super().__init__()
        self.get_amount_min: Callable[[], float]
        self.get_amount_max: Callable[[], float]
        self.get_date_from: Callable[[], int]
        self.get_date_to: Callable[[], int]

    def get_fields(self) -> List[str]:
        return [
            "amount_min",
            "amount_max",
            "date_from",
            "date_to",
            "description_regex"
        ]

    def get_data_transform_map(self) -> Dict[str, Callable[[str], Any]]:
        return {
            "amount_min": float,
            "amount_max": float,
            "date_from": DateValue.ddmmyy_to_timestamp,
            "date_to": DateValue.ddmmyy_to_timestamp,
        }
