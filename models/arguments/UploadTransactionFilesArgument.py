from PersonalFinanceCLI.models.arguments.BaseArgument import BaseArgument
class UploadTransactionFilesArgument(BaseArgument):

    def __init__(self) -> None:
        self.verify = {
            "accountNumber" : self.validateFolderOrFile
        }

        self.non_mandatory = ["folder","file"]
        self.fields = [
            "accountNumber",
            "folder",
            "file"
        ]
        super().__init__()
        self.GetaccountNumber().help("Account Number")
        self.Getfolder().help("Transactions Folder")
        self.Getfile().help("Transaction File(Will be ignored if Folder is provided)")

    def validateFolderOrFile(self,x):
        if self.Getfolder()==None and self.Getfile() == None:
            print("Please provide Folder name/File name")
            return False
        return True