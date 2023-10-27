'''Process the amount lines in a statement'''
from decimal import Decimal, InvalidOperation
from typing import List, Optional
from statement_file_processor.processors.statement_processors.line_processors.regex_line_processor\
    import RegexLineProcessor
from statement_file_processor.data_types.amount_value import AmountValue
from statement_file_processor.data_types.type_enums import TransactionType


class AmountLineProcessor(RegexLineProcessor):
    '''Process the amount lines in a statement'''

    def __init__(self, processor_name: str = "amount"):
        RegexLineProcessor.__init__(self, processor_name)
        # TODO Change "." not being present in the amount to no match regex
        self.set_fetch_value_from_line_function(self.process_amount)

    def process_amount(self, line: str) -> Optional[AmountValue]:
        '''Extract the amount from given line'''
        try:
            # Replace the commans in amount values if present and then split them
            line_values = line.upper().replace(',', '').split(' ')
            # To seperate integers which may not be amounts ignoring any  line value without '.'
            # For eg: Feature points may come along with amount but they will not have . decimals
            if "." not in line_values[0]:
                return None
            amount_value = AmountValue()\
                .amount(Decimal(line_values[0])) \
                .transaction_type(TransactionType.DEBIT) \
                .negative_entry(False)
            if len(line_values) > 1 and line_values[1] == 'CR':
                amount_value.transaction_type(TransactionType.CREDIT)
            if amount_value.get_amount() < 0:
                amount_value.amount(0-amount_value.get_amount())
                amount_value.negative_entry(True)
                if amount_value.get_transaction_type() == TransactionType.CREDIT:
                    amount_value.transaction_type(TransactionType.DEBIT)
                else:
                    amount_value.transaction_type(TransactionType.CREDIT)
            return amount_value
        except InvalidOperation:
            return None

    def get_regex_line_match(self) -> List[str]:
        return [
            '([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9]'
            ]
    