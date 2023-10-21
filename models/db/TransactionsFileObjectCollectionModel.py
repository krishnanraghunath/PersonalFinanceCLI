from typing import List, Callable
from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.BaseModel import BaseModel
from PersonalFinanceCLI.models.db.Enums import TransactionFileProcessingStatus,EnumUtil
from PersonalFinanceCLI.models.transactions.DateValue import DateValue
class TransactionsFileObjectCollectionContextModel(BaseDBModel):
    '''Transaction File Object Context Model'''
    def __init__(self) -> None:
        super().__init__()
        self.get_file_type: Callable[[], str]
        self.get_total_transactions: Callable[[], int]

    def pretty_string(self) -> str:
        "Return a pretty representation of the object"
        str = ''
        if self.GetfileType():
            str = "%sFile Type => %s"%(str,self.GetfileType())
        if self.GettotalTransactions():
            str = "%s\nTotal Transactions => %d"%(str,self.GettotalTransactions())
        return str

    def get_fields(self) -> List[str]:
        return [
            "file_type",
            "total_transactions",
        ]


class TransactionsFileObjectCollectionModel(BaseDBModel):
    CollectionName = "objects"
    def __init__(self,no_transforms=False):
        self.transforms = {
            "status" : lambda x:EnumUtil.convert_enum_value_to_text(x,TransactionFileProcessingStatus)
        }
        
        self.fields = 
        self.hashfields = [
            "fileKey"
        ]
        self.printtable = {
           "accountNumber": "Account Number",
            "fileKey" : "File Key",
            "fileLoc": "File Location",
            "fileObject": "File Object",
            "status": "Status",
            "createdtimestamp":"Created Timestamp",
            "lastmodifiedtimestamp":"Last Modified Timestamp",
            "context" : "Context",
            "error": "File Error String",
        }
        self.printfunc = {
            "createdtimestamp" : lambda x: DateValue.date_to_string(x),
            "lastmodifiedtimestamp" : lambda x: DateValue.date_to_string(x),
            "fileLoc" : lambda x: "..."+x[-20:],
            # "context" : lambda x: ContextToString(x)
        }
        super().__init__(no_transforms)

        # def ContextToString(x):
           

    def get_fields(self) -> List[str]:
        return [
            "account_number",
            "file_key",
            "file_location",
            "file_object",
            "status",
            "error",
            "created_timestamp",
            "last_modified_timestamp",
            "context"
        ]