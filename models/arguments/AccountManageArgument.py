from PersonalFinanceCLI.models.arguments.BaseArgument import BaseArgument
from PersonalFinanceCLI.models.db.Enums import EnumUtil, Banks,AccountType
class AccountManageArgument(BaseArgument):

    def __init__(self) -> None:
        self.verify = {
            "account" : lambda x: x!= None and len(x) > 1,
            "bank" : lambda x: EnumUtil.isEnumValue(x,Banks),
            "type" : lambda x: EnumUtil.isEnumValue(x,AccountType),
            "name" : lambda x: len(x) > 5

        }
        self.fields = [
            "account",
            "bank",
            "type",
            "name"
        ]
        super().__init__()
        self.Getaccount().help("Account Number")
        self.Getbank().help("Account Bank")
        self.Gettype().help("Account Type")
        self.Getname().help("Account Name")
