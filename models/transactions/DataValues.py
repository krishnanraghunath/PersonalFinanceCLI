from PersonalFinanceCLI.models.BaseModel import BaseModel
class DataValues(BaseModel):
    def __init__(self):
        self.fields = [
            "values",
            "count"
        ]        
        super().__init__()

    
        