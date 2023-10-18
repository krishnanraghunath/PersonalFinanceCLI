from PersonalFinanceCLI.models.db.TransactionsFileObjectCollectionModel import \
    TransactionsFileObjectCollectionModel,TransactionsFileObjectCollectionContextModel
from PersonalFinanceCLI.models.db.Enums import TransactionFileProcessingStatus
from PersonalFinanceCLI.db.BaseDBClient import BaseDBClient
from hashlib import md5
from time import time
class UploadTransactionsFilesClient(BaseDBClient):
    def __init__(self) -> None:
        super().__init__(TransactionsFileObjectCollectionModel)
        pass

    def create_file(self,accountNumber,fileContent,fileType,filePath):
        return self.insert(
            TransactionsFileObjectCollectionModel()
                .accountNumber(accountNumber)
                .fileKey(md5(fileContent).hexdigest())
                .fileLoc(filePath)
                .fileObject(fileContent)
                .status(TransactionFileProcessingStatus.CREATED)
                .createdtimestamp(int(time())*1000)
                .lastmodifiedtimestamp(int(time()*1000))
                .context(
                    TransactionsFileObjectCollectionContextModel().fileType(fileType))
        )
    
    def get_file(self,fileKey):
        return self.find_item(
                    TransactionsFileObjectCollectionModel()
                        .fileKey(fileKey))
    
    def get_newly_created_files(self):
        fileObjects = self.find_items(
                TransactionsFileObjectCollectionModel()
                    .status(TransactionFileProcessingStatus.CREATED),
                TransactionsFileObjectCollectionModel(True).fileKey(1).status(1)
                )
        if fileObjects:
            return [x.GetfileKey() for x in fileObjects]
        return []
    
    def update_status(self,key,new_status,error_string = None):
        # return True
        current_item = self.get_file(key)
        if current_item == None:
            return False 
        errorValue = None 
        if new_status == TransactionFileProcessingStatus.FAILED or \
              new_status == TransactionFileProcessingStatus.PROCESSED_PARTIAL:
            errorValue = error_string
        return self.update_item(
            TransactionsFileObjectCollectionModel()
                        .fileKey(key)
                        .status(new_status)
                        .error(errorValue)
                        .lastmodifiedtimestamp(int(time()*1000)))

    def update_total_transactions(self,key,transactionCount):
        # return True
        current_item = self.get_file(key)
        if current_item == None:
            return False 
        context = TransactionsFileObjectCollectionContextModel().ingest(current_item.Getcontext())
        return self.update_item(
            TransactionsFileObjectCollectionModel()
                        .fileKey(key)
                        .lastmodifiedtimestamp(int(time()*1000))
                        .context(context.totalTransactions(transactionCount)))
    
    def remove_file_object(self,key):
        #   return True
          return self.update_item(
            TransactionsFileObjectCollectionModel()
                        .fileKey(key)
                        .fileObject("{REMOVEDPOSTPROCESSING}"))


    
    def get_file_details(self,status,accountNumber=None):
        query_term = TransactionsFileObjectCollectionModel() \
                            .status(status)
        projected_items = TransactionsFileObjectCollectionModel(1).accountNumber(1) \
                            .status(1).error(1).fileLoc(1).createdtimestamp(1) \
                            .lastmodifiedtimestamp(1).context(1)
        items = self.find_items(query_term,projected_items)
        if items:
            [x.context(TransactionsFileObjectCollectionContextModel().ingest(x.Getcontext())) for x in items]
        return items

        
        
