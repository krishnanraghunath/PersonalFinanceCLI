from PersonalFinanceCLI.models.BaseModel import BaseModel
class DescriptionValue(BaseModel):
    def __init__(self):
        self.fields = [
            "description"
        ]
        
        super().__init__()

        
