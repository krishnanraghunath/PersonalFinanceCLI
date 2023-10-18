from PersonalFinanceCLI.models.arguments.BaseArgument import BaseArgument
# from PersonalFinanceCLI.models.db.Enums import EnumUtil,TransactionFileProcessingStatus
from PersonalFinanceCLI.models.arguments.Argument import Argument,Actions


class GetTransactionsArgument(BaseArgument):

    def __init__(self) -> None:
        self.verify = {
            "from" : lambda x:BaseArgument.validate_date_s(x),
            "to" : lambda x:BaseArgument.validate_date_s(x),
            "date" : lambda x:BaseArgument.validate_date_s(x),
            "amountgt" : lambda x:BaseArgument.validate_amount_s(x),
            "amountlt" : lambda x:BaseArgument.validate_amount_s(x),
            "amounteq" : lambda x:BaseArgument.validate_amount_s(x),
        }
        self.fields = [
            "accountNumber",
            "from",
            "to",
            "amountgt",
            "amountlt",
            "rdesc",
            "tag"
        ]
        self.non_mandatory = self.fields
        super().__init__()
        self.GetaccountNumber().action(Actions.APPEND)
        self.GetaccountNumber().help("List of Account Numbers/If empty all the available accounts will be used")
        self.Getfrom().help("Date From in DD/MM/YY format.")
        self.Getto().help("Date To in DD/MM/YY format.")
        self.Getamountgt().help("Filter transactions with Minimum Amount")
        self.Getamountlt().help("Filter transactions with Maximum Amount")
        self.Getrdesc().help("Regex matching on Description")
        self.Gettag().help("The tag name")
        

    
            



