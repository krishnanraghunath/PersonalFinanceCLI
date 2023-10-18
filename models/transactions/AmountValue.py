from PersonalFinanceCLI.models.BaseModel import BaseModel
from PersonalFinanceCLI.models.db.Enums import TransactionType,EnumUtil
from decimal import Decimal
class AmountValue(BaseModel):
    def __init__(self):
        self.transforms = {
            "amount" : lambda x: Decimal(x),
            "txnType" : lambda x:EnumUtil.valueToEnumText(x,TransactionType)
        }
        self.fields = [
            "amount",
            "txnType",
            "negativeEntry"
        ]
        super().__init__()
    
    def GetActualAmount(self):
        multiply_factor = 1 
        if self.GetnegativeEntry():
            multiply_factor = -1
        if self.GettxnType() == TransactionType.CREDIT:
            return self.Getamount()*multiply_factor
        else:
            return self.Getamount()*-1*multiply_factor
        
    
    
        