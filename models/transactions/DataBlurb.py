'''Data Blurb Model'''
from typing import List
from PersonalFinanceCLI.models.BaseModel import BaseModel


class DataBlurb(BaseModel):
    '''Data Blurb Model'''

    def __init__(self) -> None:
        super().__init__()

    def get_fields(self) -> List[str]:
        return [
            "startLine",
            "endLine"
        ]
