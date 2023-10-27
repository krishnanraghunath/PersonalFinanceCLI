'''Object holding the details regarding the transactions'''
from __future__ import annotations
from typing import List
from statement_file_processor.data_types.transaction import Transaction


class ItemDetails:
    '''Object holding the details regarding the transactions'''

    def __init__(self) -> None:
        self._transactions: List[Transaction] = []
        self._account_number: str = str()

    def with_transactions(self, transaction: List[Transaction]) -> ItemDetails:
        '''Add the transactions'''
        self._transactions.extend(transaction)
        return self

    def with_account_number(self, account_number: str) -> ItemDetails:
        '''Add the account number'''
        self._account_number = account_number
        return self

    def get_transactions(self) -> List[Transaction]:
        '''Get the list of transactions'''
        return self._transactions

    def get_account_number(self) -> str:
        '''Get the account number'''
        return self._account_number