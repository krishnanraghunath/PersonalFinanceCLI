from PersonalFinanceCLI.models.BaseModel import BaseModel
class DataValue(BaseModel):
    def __init__(self):
        self.fields = [
            "value",
            "line"
        ]        
        super().__init__()

    
        