'''Amount Value Model (amount, type of amount and negative entry??)'''
from typing import Any, Callable, Dict, List
from decimal import Decimal
from statement_file_processor.data_types.base_type import BaseType
from statement_file_processor.data_types.type_enums import EnumUtil, TransactionType


class AmountValue(BaseType):
    '''Amount Value Model (amount, type of amount and negative entry??)'''

    def __init__(self):
        super().__init__()
        self.get_negative_entry: Callable[[], bool]
        self.get_transaction_type: Callable[[], TransactionType]
        self.get_amount: Callable[[], Decimal]
        self.amount: Callable[[Decimal], AmountValue]
        self.transaction_type: Callable[[TransactionType], AmountValue]
        self.negative_entry: Callable[[bool], AmountValue]


    def get_actual_amount(self) -> Decimal:
        '''Return the actual amount based on txn type 
            and negative entry flag'''
        multiply_factor = 1
        if self.get_negative_entry():
            multiply_factor = -1
        if self.get_transaction_type() == TransactionType.CREDIT:
            return self.get_amount()*multiply_factor
        return self.get_amount()*-1*multiply_factor

    def get_fields(self) -> List[str]:
        return [
            "amount",
            "transaction_type",
            "negative_entry"
        ]

    def get_data_transform_map(self) -> Dict[str, Callable[[str], Any]]:
        return {
            "amount": Decimal,
            "txn_type": lambda x: EnumUtil.convert_enum_value_to_text(
                x, TransactionType)
        }
