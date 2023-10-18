from PersonalFinanceCLI.db.UploadTransactionsFilesClient import UploadTransactionsFilesClient
from PersonalFinanceCLI.db.AccountCollectionClient import AccountCollectionClient
from PersonalFinanceCLI.db.TransactionCollectionClient import TransactionCollectionClient
from PersonalFinanceCLI.processors.statement_processors._processors_map import ProcessorsMapping
from PersonalFinanceCLI.models.db.Enums import TransactionFileProcessingStatus

class BasicProcessor:
    def __init__(self,fileKey):
        self.uploadtransactionsFilesClient =UploadTransactionsFilesClient()
        try:
            self.fileInfo = self.uploadtransactionsFilesClient.get_file(fileKey)
            self.uploadtransactionsFilesClient.update_status(fileKey,
                                                         TransactionFileProcessingStatus.PROCESSING)
            self.accountInfo = AccountCollectionClient() \
                                .get_account_information(self.fileInfo.GetaccountNumber())
            if self.accountInfo == None:
                raise Exception("Account Information not found for account number %d" % 
                                            self.fileInfo.GetaccountNumber())
            self.processorId =  "%s:%s:%s"%(
                        self.accountInfo.GetaccountBank(),
                        self.accountInfo.GetaccountType(),
                        self.fileInfo.Getcontext()["fileType"]
                     )
            self.transactionsClient = TransactionCollectionClient()
        except Exception as e:
            self.processorId = None
            self.uploadtransactionsFilesClient.update_status(fileKey,
                                                         TransactionFileProcessingStatus.FAILED,
                                                         "Unknown Error -> %s"%str(e))
            

    def process(self):
        if self.processorId not in ProcessorsMapping:
            print ("No processors found for the account -> %s"%self.processorId)
            self.uploadtransactionsFilesClient.update_status(self.fileInfo.GetfileKey(),
                                                         TransactionFileProcessingStatus.FAILED,
                                                         "No processors found for the account -> %s"%self.processorId)
            return False,None
        
        processor = ProcessorsMapping[self.processorId](self.fileInfo,self.accountInfo)
        if processor.initialise():
            print("Processing file %s with Processor => %s"%(self.fileInfo.GetfileLoc(),self.processorId))
            response,transactions = processor.process()
            self.uploadtransactionsFilesClient.update_total_transactions(self.fileInfo.GetfileKey(),
                                                                                 len(transactions))
            if response:
                print ("success")
                return
                res,failed = self.transactionsClient.insert_transactions(transactions)
                print("Found %d Saved %d"%(len(transactions),len(transactions) - len(failed)))
                if res:
                    self.uploadtransactionsFilesClient.update_status(self.fileInfo.GetfileKey(),
                                                         TransactionFileProcessingStatus.PROCESSED)
                    self.uploadtransactionsFilesClient.remove_file_object(self.fileInfo.GetfileKey())
                    return True
                else:
                    print("------Failed Transactions-----")
                    for failTransaction in failed:
                        print(~failTransaction)
                    print("------------------------------")
                    self.uploadtransactionsFilesClient.update_status(self.fileInfo.GetfileKey(),
                                                         TransactionFileProcessingStatus.PROCESSED_PARTIAL,
                                                         "Failed to save %d entries"%len(failed))
            else:
                print("Failed to Process.")
                return
                self.uploadtransactionsFilesClient.update_status(self.fileInfo.GetfileKey(),
                                                         TransactionFileProcessingStatus.FAILED,
                                                         "Processing Errors with File.")
        return False
       
