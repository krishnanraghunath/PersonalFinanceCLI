import argparse
from PersonalFinanceCLI.models.arguments.AccountManageArgument import AccountManageArgument
from PersonalFinanceCLI.models.db.AccountCollectionModel import AccountCollectionModel
from PersonalFinanceCLI.db.AccountCollectionClient import AccountCollectionClient
from PersonalFinanceCLI.commands.BaseCommand import BaseCommand

class AccountManage(BaseCommand):
    def __init__(self,cmdLineArgs):
        self.arguments = AccountManageArgument()
        super().__init__(self.arguments,cmdLineArgs)
        self.arguments.validate()
        self.accountCollectionClient = AccountCollectionClient()
    
    def _run(self):
       if self.accountCollectionClient.create_account( 
                                                    AccountCollectionModel().
                                                    accountNumber(self.arguments.Getaccount()).
                                                    accountName(self.arguments.Getname()).
                                                    accountBank(self.arguments.Getbank()).
                                                    accountType(self.arguments.Gettype())):
           print("Account has been created succesfully!")
       else:
           print("Error occured while creating the account!!")
       