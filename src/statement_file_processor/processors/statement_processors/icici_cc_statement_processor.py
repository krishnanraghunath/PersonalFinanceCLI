'''ICICI Credit Card statement processor'''
from decimal import Decimal
from typing import List, Tuple, cast
from functools import partial
from statement_file_processor.data_types.date_value import DateValue
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.processors.statement_processors.line_processors.\
    amount_line_processor import AmountLineProcessor
from statement_file_processor.processors.statement_processors.line_processors.\
    regex_line_processor import RegexLineProcessor
from statement_file_processor.processors.statement_processors.pdf_statement_processor\
    import PDFStatementProcessor
from statement_file_processor.data_types.transaction import Transaction
from statement_file_processor.data_types.type_enums import TransactionType
from statement_file_processor.data_types.card_number_value import CardNumberValue
from statement_file_processor.data_types.description_value import DescriptionValue


def _replace(x: str) -> str:
    '''Replace ` with empty in the given string'''
    return x.replace('`', '')


class ICICICCStatementProcessor(PDFStatementProcessor):
    '''ICICI Credit Card statement processor'''

    def __init__(self):
        PDFStatementProcessor.__init__(self)
        # For taking care of transactions being duplicated. Lucky we have this serial number
        self.serial_number_processor = RegexLineProcessor("serial")
        self.statement_amount_line_processor = AmountLineProcessor("statement")

        self.statement_amount_line_processor.\
            set_pre_process_line_function(_replace)

        self.regex_line_processor_account_details.set_fetch_value_from_line_function(
            CardNumberValue().card_number)

    def load_config(self, json_config_file_name: str) -> None:
        super().load_config(json_config_file_name)
        self.load_config_for_processor(self.statement_amount_line_processor)
        self.load_config_for_processor(self.serial_number_processor)

    def remove_duplicate_entries(self) -> None:
        '''Remove the current transactions of duplcates based on serials'''
        serial_numbers_value: List[str] = [cast(DescriptionValue, x.get_value())
                                           .get_description() for x in
                                           self.serial_number_processor.get_data_values()]
        index_to_remove: List[int] = []
        serial_numbers: List[str] = []
        for _data_value_index in range(self.serial_number_processor.get_total_data_values()):
            # If serial number have already encountered, then remove the same data value
            if serial_numbers_value[_data_value_index] in serial_numbers:
                index_to_remove.append(_data_value_index)
            else:
                serial_numbers.append(serial_numbers_value[_data_value_index])

        # Remove the item and each time the indices of all the subsequent elements will get decremenetd by 1
        removed_indices = 0
        for i in index_to_remove:
            self.line_processor_amount.remove(i - removed_indices)
            self.line_processor_date.remove(i - removed_indices)
            self.line_processor_description.remove(i - removed_indices)
            self.serial_number_processor.remove(i - removed_indices)
            removed_indices = removed_indices + 1

    def process(self, queue_item: QueueItem) -> Tuple[bool, str, List[Transaction]]:
        file_content = queue_item.get_file_content()
        if file_content is None:
            return False, "File content is None", []
        for line in file_content.splitlines():
            self.line_processor_amount.process(line)
            self.line_processor_date.process(line)
            self.line_processor_description.process(line)
            self.regex_line_processor_account_details.process(line)
            self.statement_amount_line_processor.process(line)
            self.serial_number_processor.process(line)

        # Checking we have right data to proceed
        amount_count = self.line_processor_amount.get_total_data_values()
        descriptions_count = self.line_processor_description.get_total_data_values()
        dates_count = self.line_processor_date.get_total_data_values()
        serial_number_count = self.serial_number_processor.get_total_data_values()
        account_details_count = self.regex_line_processor_account_details.get_total_data_values()
        statement_amount_count = self.statement_amount_line_processor.get_total_data_values()

        # # TODO: Remove below lines
        # for i in self.line_processor_date.get_data_values():
        #     print(DateValue.date_to_string(i.get_value().get_date()))
        # for i in self.line_processor_description.get_data_values():
        #     print(i.get_value().get_description())
        # for i in self.line_processor_amount.get_data_values():
        #     print(i.get_value().get_amount())
        # print(dates_count)
        # print(descriptions_count)
        # print(amount_count)
        # # TODO: Remove above lones


        # 1. Check if all the collected data is of same count
        if len(set([amount_count, descriptions_count, dates_count, serial_number_count])) != 1:
            return False, "Unable to proceed because the collected data length differs", []
        # 2. Check if we have collected required number of account details
        if account_details_count < 1:
            return False, "Unable to proceed because account details were not collected properly", []
        # 3. Check if we have captured required numnber of statement amounts
        if statement_amount_count != 5:
            return False, "Unable to proceed because statement aggragate amount details\
                                were not collected properly", []

        # In some special case the transactions recorded seems to be getting repeated. taking care
        # of such situation.
        # Basically the collected serial number will be used to remove duplicate transactions since,
        # serial number are uniq to each row/transaction
        self.remove_duplicate_entries()

        # Checking the statement section
        statement_aggragate_amounts_transaction_types: List[TransactionType] = [x.get_value().get_transaction_type() for x in  # type: ignore
                                                                                self.statement_amount_line_processor.get_data_values()[:2]]
        statement_aggragate_amounts: List[Decimal] = [x.get_value().get_amount() for x in  # type: ignore
                                                      self.statement_amount_line_processor.get_data_values()[:5]]
        total_due, previous_due, total_expenditures, total_cash, total_payments = statement_aggragate_amounts
        total_due_transaction_type, previous_due_transaction_type = statement_aggragate_amounts_transaction_types
        # If Previous Due is CR (Credit), means a positive due, same is applicable for Total Due
        if previous_due_transaction_type == TransactionType.CREDIT:
            previous_due = 0 - previous_due
        if total_due_transaction_type == TransactionType.CREDIT:
            total_due = 0 - total_due
        # Final cros verification of values collected
        if total_due != (previous_due + total_expenditures + total_cash - total_payments):
            return False, "Unable to match amounts in statements. Debug with the said statement", []

        # Now that we can use totalExpenditures and totalPayments to verify Transaction Section
        # Cross checking statement amounts and parsed transaction amounts/details
        total_payments_calculated, total_expenditures_calculated = self.get_total_credits_debits()
        if total_payments != total_payments_calculated or \
                total_expenditures != total_expenditures_calculated:
            return False, "Unable to match statement summary amount and calculated amounts\
                  from Parsed data. Debug with the said file", []
        return True, self.get_card_details(), self.get_transactions()
