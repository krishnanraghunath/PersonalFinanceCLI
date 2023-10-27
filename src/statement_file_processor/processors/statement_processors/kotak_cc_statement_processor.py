'''Processing Kotak Credit Card statement'''
from decimal import Decimal
from typing import List, Optional, Tuple, cast
from statement_file_processor.data_types.data_value import DataValueType
from statement_file_processor.data_types.amount_value import AmountValue
from statement_file_processor.data_types.card_number_value import CardNumberValue
from statement_file_processor.data_types.date_value import DateValue
from statement_file_processor.data_types.description_value import DescriptionValue
from statement_file_processor.data_types.transaction import Transaction
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.processors.statement_processors.pdf_statement_processor\
    import PDFStatementProcessor

def _process_card_number(line: str) -> Optional[CardNumberValue]:
    '''Process the card number from given line'''
    try:
        return CardNumberValue().card_number(line.split(' ')[-1])
    except AttributeError:
        return None
    except IndexError:
        return None
        
class KotakCCStatementProcessor(PDFStatementProcessor):
    '''Processing Kotak Credit Card statement'''

    IGNORE_PAYMENTS_ENTRY = [
        'PAYMENT RECEIVED-MOBILE FUNDS TRANSFER',
        'PAYMENT RECEIVED-NEFT',
        'PAYMENT RECEIVED-KOTAK IMPS',
        'CRED',
    ]
    ANNUAL_STATEMENT_DESCS = [
        'GST',
        'ANNUAL FEE'
    ]

    def __init__(self):
        PDFStatementProcessor.__init__(self)
        self.regex_line_processor_account_details.\
            set_fetch_value_from_line_function(_process_card_number)

    def get_calculated_dues_from_transactions(self, transactions: List[Transaction]) -> Decimal:
        ''' Finding current months debits and credits other than NEFT or Payments 
        to match up the due amount. This is specific for
        Kotak Credit Card only!!
        '''
        current_dues = Decimal(0)
        for _transaction in transactions:
            if _transaction.get_description() not in\
                    KotakCCStatementProcessor.IGNORE_PAYMENTS_ENTRY:
                # Reducing the actual amount (- credit (debits from credit card)
                #  + debits (refunds))
                current_dues = current_dues - _transaction.get_actual_amount()
        return current_dues

    def process(self, queue_item: QueueItem) -> Tuple[bool, str, List[Transaction]]:
        file_content = queue_item.get_file_content()
        if file_content is None:
            return False, "File content is None", []
        for line in file_content.splitlines():
            self.line_processor_amount.process(line)
            self.line_processor_date.process(line)
            self.line_processor_description.process(line)
            self.regex_line_processor_account_details.process(line)

        # Verifying values
        amount_count = self.line_processor_amount.get_total_data_values()
        descriptions_count = self.line_processor_description.get_total_data_values()
        dates_count = self.line_processor_date.get_total_data_values()
        account_details_count = self.regex_line_processor_account_details.get_total_data_values()
       
        # In some cases there will be no credit card number in the statement
        # following flags are for handling such cases
        annual_statement = False
        only_payments = False
        # 1. Verify account details are present or not
        # For annual fees statement the card details may not be present.
        # If only payments are done then card details may not be present
        if account_details_count == 0:
            # Checking if annual statement description is present or not
            _annual_statement_descriptions = [
                cast(DescriptionValue, x.get_value()).get_description() not in
                KotakCCStatementProcessor.ANNUAL_STATEMENT_DESCS for x in
                self.line_processor_description.get_data_values()]
            # Checking if non payment entries are present in the card
            _non_payment_descriptions = [
                cast(DescriptionValue, x.get_value()).get_description() not in
                KotakCCStatementProcessor.IGNORE_PAYMENTS_ENTRY for x in
                self.line_processor_description.get_data_values()]
            if True not in _annual_statement_descriptions:
                annual_statement = True
            elif True not in _non_payment_descriptions:
                only_payments = True
            else:
                return False, "Unable to fetch account details!", []

        # 2 Verify the data lengths
        # 2.(1) Dates count and descriptions count should be same
        if dates_count != descriptions_count:
            return False, "Date and Descriptions count do not matches!", []
        # 2.(2) Amount should have an extra value for subtotal
        if (amount_count - dates_count) != 1:
            return False, "Amount values Count is not as expecteds!", []

        # Creating the transaction entries
        _transactions = self.get_transactions()

        # 3 Verify the total dues
        # Total amount is the last value in amount data ( check 2.(2) for the verification)
        total_due_as_per_statement = cast(AmountValue,
                                          self.line_processor_amount.get_data_values()[-1].get_value()).\
            get_amount()
        total_due_as_per_transactions = self.get_calculated_dues_from_transactions(
            _transactions)
        if total_due_as_per_transactions != total_due_as_per_statement:
            return False, "Unable to match Due amount with that of calculated one from captured transaction", []

        card_number = ''
        if annual_statement:
            card_number = "KOTAK_CREDIT_CARD_ANNUAL_STATEMENTS"
        elif only_payments:
            card_number = "KOTAK_CREDIT_CARD_ONLY_PAYMENTS"
        else:
            card_number = self.get_card_details()
        return True, card_number, _transactions
