from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.BaseModel import BaseModel
from PersonalFinanceCLI.models.db.Enums import TransactionFileProcessingStatus,EnumUtil
from PersonalFinanceCLI.models.transactions.DateValue import DateValue
class TransactionsFileObjectCollectionContextModel(BaseDBModel):
    def __init__(self) -> None:
        self.fields = [
            "fileType",
            "totalTransactions",
        ]
        super().__init__()

    def PrettyString(self):
        str = ''
        if self.GetfileType():
            str = "%sFile Type => %s"%(str,self.GetfileType())
        if self.GettotalTransactions():
            str = "%s\nTotal Transactions => %d"%(str,self.GettotalTransactions())
        return str
                    


class TransactionsFileObjectCollectionModel(BaseDBModel):
    CollectionName = "objects"
    def __init__(self,no_transforms=False):
        self.transforms = {
            "status" : lambda x:EnumUtil.valueToEnumText(x,TransactionFileProcessingStatus)
        }
        
        self.fields = [
            "accountNumber",
            "fileKey",
            "fileLoc",
            "fileObject",
            "status",
            "error",
            "createdtimestamp",
            "lastmodifiedtimestamp",
            "context"
        ]
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
            "createdtimestamp" : lambda x: DateValue.DateToString(x),
            "lastmodifiedtimestamp" : lambda x: DateValue.DateToString(x),
            "fileLoc" : lambda x: "..."+x[-20:],
            # "context" : lambda x: ContextToString(x)
        }
        super().__init__(no_transforms)

        # def ContextToString(x):
           

    