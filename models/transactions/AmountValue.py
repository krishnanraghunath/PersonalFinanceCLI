'''Amount Value Model (amount, type of amount and negative entry??)'''
from typing import Any, Callable, Dict, List
from decimal import Decimal
from PersonalFinanceCLI.models.BaseModel import BaseModel
from PersonalFinanceCLI.models.db.Enums import TransactionType, EnumUtil


class AmountValue(BaseModel):
    '''Amount Value Model (amount, type of amount and negative entry??)'''

    def __init__(self):
        super().__init__()
        self.get_negative_entry: Callable[[], bool]
        self.get_txn_type: Callable[[], TransactionType]
        self.get_amount: Callable[[], Decimal]

    def get_actual_amount(self) -> Decimal:
        '''Return the actual amount based on txn type 
            and negative entry flag'''
        multiply_factor = 1
        if self.get_negative_entry():
            multiply_factor = -1
        if self.get_txn_type() == TransactionType.CREDIT:
            return self.get_amount()*multiply_factor
        else:
            return self.get_amount()*-1*multiply_factor

    def get_fields(self) -> List[str]:
        return [
            "amount",
            "txn_type",
            "negative_entry"
        ]

    def get_data_transform_map(self) -> Dict[str, Callable[[str], Any]]:
        return {
            "amount": Decimal,
            "txn_type": lambda x: EnumUtil.convert_enum_value_to_text(
                x, TransactionType)
        }
