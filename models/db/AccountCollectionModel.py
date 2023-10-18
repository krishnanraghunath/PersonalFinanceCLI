from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.db.Enums import AccountType,Banks,EnumUtil
class AccountCollectionModel(BaseDBModel):
    CollectionName = "accounts"
    def __init__(self):
        self.transforms = {
            "accountBank" : lambda x:EnumUtil.valueToEnumText(x,Banks),
            "accountType" : lambda x:EnumUtil.valueToEnumText(x,AccountType)
        }
        self.fields = [
            "accountNumber",
            "accountName",
            "accountBank",
            "accountType",
        ]
        self.hashfields = [
            "accountNumber"
        ]
        super().__init__()
    