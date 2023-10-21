'''Mongo DB Query Model'''
from typing import List
from PersonalFinanceCLI.models.BaseModel import BaseModel


class MongoDBQueryModel(BaseModel):
    '''Mongo DB Query Model'''

    def __init__(self) -> None:
        BaseModel.__init__(self)
        # .in seems to be problem as a function. removing it
        setattr(self, "In", self._function_set('_in'))

    def get_key_appender(self) -> str:
        return '$'

    def get_fields(self) -> List[str]:
        return [
            "gt",
            "lt",
            "regex",
            "in"
        ]