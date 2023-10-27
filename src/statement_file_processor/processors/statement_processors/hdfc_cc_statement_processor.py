
from decimal import Decimal
from typing import List, Tuple, cast
from statement_file_processor.data_types.amount_value import AmountValue
from statement_file_processor.data_types.card_number_value import CardNumberValue
from statement_file_processor.data_types.date_value import DateValue
from statement_file_processor.data_types.transaction import Transaction
from statement_file_processor.data_types.type_enums import TransactionType
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.processors.statement_processors.common import HDFC_CC_STATEMENT_PROCESSOR
from statement_file_processor.processors.statement_processors.line_processors.amount_line_processor import AmountLineProcessor
from statement_file_processor.processors.statement_processors.pdf_statement_processor import PDFStatementProcessor


def _process_card_number(line: str) -> CardNumberValue:
    return CardNumberValue().card_number(
        ''.join(line.split('Card No:')[1].split(' ')))


class HDFCCCStatementProcessor(PDFStatementProcessor):
    '''Processing HDFC Statement'''

    HDFC_DUE_ERROR_THRESHOLD = 50
    HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD = 25

    def __init__(self):
        PDFStatementProcessor.__init__(self)
        self.line_processor_statement_amount = AmountLineProcessor("statement")
        self.regex_line_processor_account_details.\
            set_fetch_value_from_line_function(_process_card_number)

    def load_config(self, json_config_file_name: str) -> None:
        super().load_config(json_config_file_name)
        self.load_config_for_processor(self.line_processor_statement_amount)

    def search_for_descriptions_between_date_amount_blurbs(self, blurb_index: int,
                                                           lines: str) -> None:
        '''Search for description between given date value and amount value'''
        date_blobs = self.line_processor_date.get_blurbs_of_continuous_lines()
        amount_blobs = self.line_processor_amount.get_blurbs_of_continuous_lines()
        try:
            description_search_start = date_blobs[blurb_index].get_end_line()
            description_search_end = amount_blobs[blurb_index].get_start_line()
            self.line_processor_description.set_line_counter(
                description_search_start)
            self.line_processor_description.force_process_lines(
                lines.splitlines()
                [description_search_start:description_search_end]
            )
            self.line_processor_description.re_organize()
        except IndexError:
            pass

    def get_calculated_amounts(self) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        ''' We have basically 4 types of transaction in statement
         a) -> Debit eg: 800.00
         b) -> Credit eg: 800.00 CR
         c) -> Negative Credit eg: -800.00 (Seeing - the transaction type will be toggled)
         d) -> Positive Debit eg: -800.00 CR (Seeing - the transaction type will be toggled) 
         Function will return all these values post aggragation
        '''
        # This would be the sum of all the credit amounts (payment made towards the card)
        total_credit = Decimal(0)
        # This would be the sum of al the debits (actual credit card usage)
        total_debit = Decimal(0)

        # These is the sum of all the "-(amount)" transactions i.e
        total_negative_credit = Decimal(0)
        # These is the sum of all the "-(amount) CR" transactions
        total_positive_debit = Decimal(0)

        for _amount in self.line_processor_amount.get_data_values():
            amount = cast(AmountValue, _amount.get_value())
            if amount.get_transaction_type() == TransactionType.CREDIT:
                total_credit = total_credit + amount.get_amount()
                if amount.get_negative_entry():
                    total_positive_debit = total_positive_debit + amount.get_amount()
            if amount.get_transaction_type() == TransactionType.DEBIT:
                total_debit = total_debit + amount.get_amount()
                if amount.get_negative_entry():
                    total_negative_credit = total_negative_credit + amount.get_amount()
        print(total_negative_credit, total_positive_debit,
              total_credit, total_debit)
        return (total_negative_credit, total_positive_debit, total_credit, total_debit)

    def process(self, queue_item: QueueItem) -> Tuple[bool, str, List[Transaction]]:
        file_content = queue_item.get_file_content()
        if file_content is None:
            return False, "File content is None", []

        for line in file_content.splitlines():
            self.line_processor_amount.process(line)
            self.line_processor_date.process(line)
            self.line_processor_description.process(line)
            self.regex_line_processor_account_details.process(line)
            self.line_processor_statement_amount.process(line)

        # Verifying the values
        amount_count = self.line_processor_amount.get_total_data_values()
        descriptions_count = self.line_processor_description.get_total_data_values()
        dates_count = self.line_processor_date.get_total_data_values()
        account_details_count = self.regex_line_processor_account_details.get_total_data_values()
        statement_amount_count = self.line_processor_statement_amount.get_total_data_values()

        # 1. Verify the data lengths

        # 1.(a) verify dates count and amount count
        if dates_count != amount_count:
            return False, "Failed to get all entries.Mismatch in Dates and Amounts", []

        # 1. (b) verify the description line count matches with others

        # Handling an edge case where the description comes in between last date and amout entries
        if descriptions_count < amount_count:
            # Case 1 -> A section of description got skipped between
            # the  last blurbs of amounts & dates
            self.search_for_descriptions_between_date_amount_blurbs(-1,
                                                                    file_content)
            # Case 2 -> A section of description got skipped between the
            # second last blurbs of amounts & dates
            self.search_for_descriptions_between_date_amount_blurbs(-2,
                                                                    file_content)

        if descriptions_count != amount_count:
            return False, "Mismatch in Description and Amounts", []

        # 2 Verify statement amount count
        if statement_amount_count != 5:
            return False, "Error in getting proper statement values", []

        # 3. Check if we have collected required number of account details
        if account_details_count < 1:
            return False, "Unable to proceed because account details were\
                            not collected properly", []

        statement_amounts = self.line_processor_statement_amount.get_data_values()
        # Get the statement summary values
        opening_balance = cast(
            AmountValue, statement_amounts[0].get_value()).get_amount()
        payments = cast(
            AmountValue, statement_amounts[1].get_value()).get_amount()
        debits = cast(
            AmountValue, statement_amounts[2].get_value()).get_amount()
        finance = cast(
            AmountValue, statement_amounts[3].get_value()).get_amount()
        total_dues = cast(
            AmountValue, statement_amounts[4].get_value()).get_amount()
        if cast(AmountValue, statement_amounts[0].get_value()).get_negative_entry():
            opening_balance = 0 - opening_balance
        if cast(AmountValue, statement_amounts[4].get_value()).get_negative_entry():
            total_dues = 0 - total_dues

        # Observed an error with error credit
        bank_error_credit, bank_error_debit, calculated_payments, calculated_debits =\
            self.get_calculated_amounts()

        # Calculate the Total Due as per statement
        total_due_calculated_without_bank_error = opening_balance - \
            payments + debits + finance
        # Calculated the Total Due taking bank error in to account
        total_due_calculated_with_bank_error = total_dues - \
            bank_error_debit + bank_error_credit
        # Now check the difference between both
        amount_calculation_difference = total_due_calculated_with_bank_error - \
            total_due_calculated_without_bank_error
        extra_payments_or_debits = Decimal(0)
        # See if the calculated payments to be made based on the transactions
        #  and the as rquested by the statement is within
        # the given threshold
        if abs(payments - calculated_payments) <\
                HDFCCCStatementProcessor.HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD:
            if abs(payments - calculated_payments) != 0:
                extra_payments_or_debits = extra_payments_or_debits + payments - calculated_payments
        else:
            return False, "Mismatch in collected summary of statements and summary", []
        # See if the calculated debits to be made based on the transactions
        #  and the as rquested by the statement is within
        # the given threshold
        if abs(debits + finance - calculated_debits) <\
                HDFCCCStatementProcessor.HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD:
            if abs(debits + finance - calculated_debits) != 0:
                extra_payments_or_debits = extra_payments_or_debits - \
                    (debits + finance - calculated_debits)
        else:
            # Removing finance from the equation and redoing it again!
            # But Why?? (Mukesh.jpg)
            # ==> Sometimes statements gets it wrong!
            if abs(debits - calculated_debits) <\
                    HDFCCCStatementProcessor.HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD:
                if abs(debits-calculated_debits) != 0:
                    extra_payments_or_debits = extra_payments_or_debits - \
                        (debits-calculated_debits)
            else:
                return False, "Mismatch in collected summary of statements and summary", []
        # Verify the difference between total due calculated and the statement
        # total due is within the threshold
        if abs(amount_calculation_difference) >\
                HDFCCCStatementProcessor.HDFC_DUE_ERROR_THRESHOLD:
            # Again!!
            # Adding finance from the equation and redoing it again!
            # But Why?? (Mukesh.jpg)
            # ==> Sometimes statements gets it wrong!
            if abs(abs(amount_calculation_difference) - finance) > \
                    HDFCCCStatementProcessor.HDFC_DUE_ERROR_THRESHOLD:
                return False, f"Mismatch in collected summary of payments ->\
                  {amount_calculation_difference}", []

        _transactions = self.get_transactions()
        # Add an extra Entry Credit/Debit to adjust small difference
        # under threshold (Not the issue with
        # programme but with the statement itself)
        if abs(extra_payments_or_debits) > 0:
            _extra_transaction = Transaction().\
                date(
                    cast(DateValue, self.line_processor_date.
                         get_data_values()[-1].get_value()).get_date()).\
                description("STATEMENT ROUNDOFF PAYMENT ADJUSTMENT").\
                amount(abs(extra_payments_or_debits)).\
                transaction_type(TransactionType.CREDIT)
            if extra_payments_or_debits < 0:
                _extra_transaction.transaction_type(TransactionType.DEBIT)
            _transactions.append(_extra_transaction)
        return True, self.get_card_details(), _transactions
