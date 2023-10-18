from PersonalFinanceCLI.models.db.AccountCollectionModel import AccountCollectionModel
from PersonalFinanceCLI.db.BaseDBClient import BaseDBClient
class AccountCollectionClient(BaseDBClient):
    def __init__(self) -> None:
        super().__init__(AccountCollectionModel)
        pass

    def create_account(self,account):
        return self.insert(account)
    
    def get_account_information(self,accountNumber):
        return self.find_item(
                AccountCollectionModel().accountNumber(accountNumber))
              
