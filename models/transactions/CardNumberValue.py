from PersonalFinanceCLI.models.BaseModel import BaseModel
class CardNumberValue(BaseModel):
    def __init__(self):
        self.fields = [
            "cardNumber"
        ]
        
        super().__init__()

        
