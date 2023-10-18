from PersonalFinanceCLI.models.arguments.TransactionFileStatusArgument import TransactionFileStatusArgument
from PersonalFinanceCLI.db.UploadTransactionsFilesClient import UploadTransactionsFilesClient
from PersonalFinanceCLI.db.AccountCollectionClient import AccountCollectionClient
from PersonalFinanceCLI.commands.BaseCommand import BaseCommand
from PersonalFinanceCLI.models.db.TransactionsFileObjectCollectionModel import TransactionsFileObjectCollectionModel

class TransactionFilesStatus(BaseCommand):
    def __init__(self,cmdLineArgs):
        self.arguments = TransactionFileStatusArgument()
        super().__init__(self.arguments,cmdLineArgs)
        self.arguments.validate()
        self.accountCollectionClient = AccountCollectionClient()
    
    def _run(self):
        self.tableSet(TransactionsFileObjectCollectionModel)
        print_columns = TransactionsFileObjectCollectionModel().accountNumber(1). \
                                            status(1).fileLoc(1).createdtimestamp(1). \
                                            lastmodifiedtimestamp(1).context(1)
        if self.arguments.GettxnStatus() in ["FAILED","PROCESSED_PARTIAL"]:
            print_columns.error(1)
        for i in UploadTransactionsFilesClient().get_file_details(
            self.arguments.GettxnStatus(),self.arguments.GetaccountNumber()
            ):
            self.tablePut(i)
        if self.arguments.GetaccountNumber() != None :
             print_columns.accountNumber(0)
        self.tablePrint(print_columns)
      