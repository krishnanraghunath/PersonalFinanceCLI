from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.db.BaseDBClient import BaseDBClient
class TransactionCollectionClient(BaseDBClient):
    def __init__(self) -> None:
        super().__init__(TransactionCollectionModel)
        pass

    def insert_transaction(self,transaction):
        self.insert(transaction)

    def insert_transactions(self,transactions):
        response,failedItems = self.insert_all(transactions)
        return response, [transactions[x['index']]._error_code(x['code']) for x in failedItems]

    
    def get_transactions(self,query,projected_items):
        return self.find_items(query,projected_items,[
            TransactionCollectionModel(1).date(1)
        ])