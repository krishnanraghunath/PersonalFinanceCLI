from PersonalFinanceCLI.models.arguments.UploadTransactionFilesArgument import UploadTransactionFilesArgument
from PersonalFinanceCLI.db.AccountCollectionClient import AccountCollectionClient
from PersonalFinanceCLI.db.UploadTransactionsFilesClient import UploadTransactionsFilesClient
from PersonalFinanceCLI.commands.BaseCommand import BaseCommand
from PersonalFinanceCLI.processors.statement_processors.common import MIME_TYPES
from os import listdir
from os.path import isfile, join
from filetype import guess

class UploadTransactionFiles(BaseCommand):
    ALLOWED_MIMES = [
        MIME_TYPES.PDF_MIME_TYPE,
        MIME_TYPES.CSV_MIME_TYPE,
        MIME_TYPES.TXT_MIME_TYPE,
        ]
    
    def get_mime(fileName):
        fileType = guess(fileName)
        if fileType == None and fileName.endswith(".csv"):
            return MIME_TYPES.CSV_MIME_TYPE
        if fileType == None and fileName.endswith(".txt"):
            return MIME_TYPES.TXT_MIME_TYPE
        if fileType != None and fileType._Type__mime in UploadTransactionFiles.ALLOWED_MIMES:
            return fileType._Type__mime
        return None

    def __init__(self,cmdLineArgs):
        self.arguments = UploadTransactionFilesArgument()
        super().__init__(self.arguments,cmdLineArgs)
        self.arguments.validate()
        self.accountCollectionClient = AccountCollectionClient()
        self.transactionsFileUploadsCollectionClient = UploadTransactionsFilesClient()
    
    def _run(self):
        if self.accountCollectionClient.get_account_information(self.arguments.GetaccountNumber()) == None:
            print("Account Number -> %s not valid!!"%self.arguments.GetaccountNumber())
        if self.arguments.Getfolder() != None:
            try:
                onlyfiles = [join(self.arguments.Getfolder(), f) for f in listdir(self.arguments.Getfolder()) 
                                    if isfile(join(self.arguments.Getfolder(), f))]
                print("Only Excel/PDF/CSV Files will be uploaded from Folder %s"
                                                        %self.arguments.Getfolder())
                results = {f:self._uploadFile(f) 
                                for f in filter(lambda y:UploadTransactionFiles.get_mime(y) != None,onlyfiles)}
                print("=====================\nEnd Results\n========================\n")
                for result in results:
                    print("%s --> \t%s"%(result,results[result]))
            except:
                import traceback 
                traceback.print_exc()
                print("Failed to get files in folder %s"%self.arguments.Getfolder())
        else:
            self._uploadFile(self.arguments.Getfile())


    def _uploadFile(self,filePath):
        try:
            print("Opening File %s"%filePath)
            fileType = UploadTransactionFiles.get_mime(filePath)
            fileContent = None
            if fileType == MIME_TYPES.TXT_MIME_TYPE:
                fileContent = open(filePath,'rb').read()
            else:
                fileContent = open(filePath,'rb').read()
    
            print("Saving File %s"%filePath)
            return self.transactionsFileUploadsCollectionClient.create_file(
                self.arguments.GetaccountNumber(),
                fileContent,
                fileType,
                filePath)
        except:
            import traceback
            traceback.print_exc()
            print("Failed to process File %s"%filePath)
        return False
        
       