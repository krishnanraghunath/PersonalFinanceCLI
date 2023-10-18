from PersonalFinanceCLI.models.arguments.BaseArgument import BaseArgument
# from PersonalFinanceCLI.models.db.Enums import EnumUtil,TransactionFileProcessingStatus
from PersonalFinanceCLI.models.arguments.Argument import Argument,Actions
from re import compile

class TagManagementArgument(BaseArgument):

    def __init__(self) -> None:
        self.verify = {
            "fromDate" : lambda x:BaseArgument.validate_date_s(x),
            "toDate" : lambda x:BaseArgument.validate_date_s(x),
            "amountgt" : lambda x:BaseArgument.validate_amount_s(x),
            "amountlt" : lambda x:BaseArgument.validate_amount_s(x)
        }
        self.fields = [
            "tagName",
            "accountNumber",
            "fromDate",
            "toDate",
            "amountgt",
            "amountlt",
            "descriptionRegex",
            "modify",
            "delete"
        ]

        self.non_mandatory =  []
        self.non_mandatory.extend(self.fields)
        self.non_mandatory.remove("tagName")
        super().__init__()
        self.GetaccountNumber().action(Actions.APPEND)
        self.Getmodify().action(Actions.STORE_TRUE)
        self.Getdelete().action(Actions.STORE_TRUE)
        self.GettagName().help("")
        self.GetaccountNumber().help("List of Account Numbers/If empty all the available accounts will be used")
        self.GetfromDate().help("Date From in DD/MM/YY format.")
        self.GettoDate().help("Date From in DD/MM/YY format.")
        self.Getamountgt().help("Filter transactions with Minimum Amount")
        self.Getamountlt().help("Filter transactions with Maximum Amount")
        self.GetdescriptionRegex().help("Regex matching on Description")
        self.Getmodify().help("To be modified if already existing")
        self.Getdelete().help("To be deleted if already existing")



