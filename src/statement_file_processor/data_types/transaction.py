'''Object denoting a single transaction'''
from __future__ import annotations
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional
from statement_file_processor.data_types.base_type import BaseType
from statement_file_processor.data_types.type_enums import TransactionType


class Transaction(BaseType):
    '''Object denoting a single transaction'''

    def __init__(self) -> None:
        BaseType.__init__(self)
        self.get_transaction_id: Callable[[], str]
        self.get_source_account_id: Callable[[], str]
        self.get_destination_account_id: Callable[[], str]
        self.get_description: Callable[[], str]
        self.get_amount: Callable[[], Decimal]
        self.get_date: Callable[[], int]
        self.get_transaction_type: Callable[[], str]
        self.get_credit: Callable[[], Decimal]
        self.get_debit: Callable[[], Decimal]
        self.credit: Callable[[Optional[Decimal]], Transaction]
        self.debit: Callable[[Optional[Decimal]], Transaction]
        self.amount: Callable[[Decimal], Transaction]
        self.transaction_type: Callable[[
            TransactionType], Transaction]
        self.transaction_id: Callable[[str], Transaction]
        self.source_account_id: Callable[[str], Transaction]
        self.destination_account_id: Callable[[
            str], Transaction]
        self.description: Callable[[str], Transaction]
        self.date: Callable[[int], Transaction]

    def refresh_credits_debits(self):
        '''Refresh the credit and debit amount based on transaction type'''
        if self.get_transaction_type() == TransactionType.CREDIT.name:
            self.credit(self.get_amount())
        if self.get_transaction_type() == TransactionType.DEBIT.name:
            self.debit(self.get_amount())

    def update_transaction_type(self):
        '''Update the type of transaction'''
        self.amount(Decimal(0.0)).transaction_type(TransactionType.DEBIT)
        amount = self.get_credit() - self.get_debit()
        self.amount(abs(amount))
        if amount < 0:
            self.transaction_type(TransactionType.DEBIT)
        else:
            self.transaction_type(TransactionType.CREDIT)
        self.credit(None).debit(None)
        return self

    def sanitise_transaction_id(self) -> Transaction:
        '''Sanitise the transaction id'''
        try:
            _transaction_id = int(self.get_transaction_id())
            if _transaction_id == 0:
                _transaction_id = int(self.get_amount())
            return self.transaction_id(str(_transaction_id))
        except ValueError:
            return self

    # def get_actual_amount(self) -> str:
    #     'Get the actual amount in string based on transaction type'''
    #     amount_prefix = '-'
    #     if self.get_transaction_type() == TransactionType.CREDIT:
    #         amount_prefix = "+"
    #     return "%s%.2f" % (amount_prefix, self.get_amount())

    def get_actual_amount(self) -> Decimal:
        '''Get the actual amount  based on transaction type'''
        _mul_factor = 1
        if self.get_transaction_type() == TransactionType.DEBIT:
            _mul_factor = -1
        return self.get_amount() * _mul_factor

    def get_fields(self) -> List[str]:
        return [
            "transaction_id",
            "source_account_id",
            "destination_account_id",
            "description",
            "amount",
            "date",
            "transaction_type",  # Should be an enum in TransactionType
            # Following fields are only for printing.
            "credit",
            "debit",
        ]

    def get_data_transform_map(self) -> Dict[str, Callable[[str], Any]]:
        return {
            "transaction_type": lambda x: x.name,  # type: ignore
            "amount": Decimal,
            "credit": Decimal,
            "debit": Decimal
        }
