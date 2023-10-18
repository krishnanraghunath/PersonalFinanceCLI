from PersonalFinanceCLI.models.BaseModel import BaseModel
class DataBlurb(BaseModel):
    def __init__(self):
        self.fields = [
            "startLine",
            "endLine"
        ]        
        super().__init__()

    
        