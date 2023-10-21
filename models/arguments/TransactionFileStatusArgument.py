from PersonalFinanceCLI.models.arguments.BaseArgument import BaseArgument
from PersonalFinanceCLI.models.db.Enums import EnumUtil,TransactionFileProcessingStatus
class TransactionFileStatusArgument(BaseArgument):

    def __init__(self) -> None:
        self.verify = {
            "txnStatus" : lambda x:EnumUtil.convert_enum_value_to_text(x,TransactionFileProcessingStatus)
        }
        self.fields = [
            "txnStatus",
            "accountNumber"
        ]
        self.non_mandatory = ["accountNumber"]
        super().__init__()
        self.GettxnStatus().help("Status can be CREATED/PROCESSED/PROCESSED_PARTIAL/FAILED")

