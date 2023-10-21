'''Base Command type for account manage'''
from typing import List, Callable
from PersonalFinanceCLI.models.arguments.AccountManageArgument import AccountManageArgument
from PersonalFinanceCLI.models.db.AccountCollectionModel import AccountCollectionModel
from PersonalFinanceCLI.db.AccountCollectionClient import AccountCollectionClient
from PersonalFinanceCLI.commands.BaseCommand import BaseCommand

class AccountManage(BaseCommand):
    '''Base Command type for account manage'''
    def __init__(self, command_line_arguments: List[str]):
        self.arguments = AccountManageArgument()
        super().__init__(self.arguments,command_line_arguments)
        self.arguments.validate()
        self.account_collection_client = AccountCollectionClient()
    
    def _run(self):
       AccountCollectionModel.accountNumber: Callable[[str], AccountCollectionModel]
       if self.account_collection_client.create_account( AccountCollectionModel(). 
                                accountNumber(self.arguments.Getaccount()). 
                                accountName(self.arguments.Getname()). \
                                accountBank(self.arguments.Getbank()). \
                                accountType(self.arguments.Gettype())):
           print("Account has been created succesfully!")
       else:
           print("Error occured while creating the account!!")
       