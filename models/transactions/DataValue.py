"Data Value Model"
from typing import List
from PersonalFinanceCLI.models.BaseModel import BaseModel


class DataValue(BaseModel):
    "Data Value Model"

    def __init__(self):
        super().__init__()

    def get_fields(self) -> List[str]:
        return [
            "value",
            "line"
        ]
