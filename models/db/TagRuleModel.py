from PersonalFinanceCLI.models.BaseModel import BaseModel
from PersonalFinanceCLI.models.transactions.DateValue import DateValue

class TagRuleModel(BaseModel):
    def __init__(self) -> None: 
        self.transforms = {
            "amountMin" : lambda x:float(x),
            "amountMax" : lambda x:float(x),
            "dateFrom" : lambda x: DateValue.DDMMYYToTimestamp(x),
            "dateTo" : lambda x: DateValue.DDMMYYToTimestamp(x),
        }
        self.fields = [
            "amountMin",
            "amountMax",
            "dateFrom",
            "dateTo",
            "descriptionRegex"
        ]
        super().__init__()
    
