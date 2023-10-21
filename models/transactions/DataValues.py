'''Date Values model'''
from typing import List
from PersonalFinanceCLI.models.BaseModel import BaseModel


class DataValues(BaseModel):
    '''Date Values model'''

    def __init__(self) -> None:
        super().__init__()

    def get_fields(self) -> List[str]:
        return [
            "values",
            "count"
        ]
