'''Description Value Model'''
from typing import List
from PersonalFinanceCLI.models.BaseModel import BaseModel


class DescriptionValue(BaseModel):
    '''Description Value Model'''

    def __init__(self):
        self.fields = [
            "description"
        ]
        super().__init__()

    def get_fields(self) -> List[str]:
        return [
            "description"
        ]
