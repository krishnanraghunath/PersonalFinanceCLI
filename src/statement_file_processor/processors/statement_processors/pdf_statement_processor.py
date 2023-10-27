'''PDF Statement Processor'''
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List, cast
from abc import ABC, abstractmethod
import logging
from json import JSONDecodeError, load as load_json_file
from statement_file_processor.data_types.amount_value import AmountValue
from statement_file_processor.data_types.card_number_value import CardNumberValue
from statement_file_processor.data_types.date_value import DateValue
from statement_file_processor.data_types.description_value import DescriptionValue
from statement_file_processor.model.queue_item import QueueItem
from statement_file_processor.processors.statement_processors.common import PDF_STATEMENT_PROCESSOR
from statement_file_processor.processors.statement_processors.line_processors.amount_line_processor\
    import AmountLineProcessor
from statement_file_processor.processors.statement_processors.line_processors.date_line_processor\
    import DateLineProcessor
from statement_file_processor.processors.statement_processors.line_processors.description_line_processor\
    import DescriptionLineProcessor
from statement_file_processor.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
from statement_file_processor.data_types.data_value import DataValue
from statement_file_processor.data_types.transaction import Transaction
from statement_file_processor.data_types.type_enums import TransactionType


class PDFStatementProcessor(ABC):
    '''PDF Statement Processor'''
    CONFIG_FOLDER = Path(__file__).parent/"statement_processor_configs"
    CARD_NOT_FOUND = "CREDIT_CARD_NUMBER_NOT_FOUND"

    def __init__(self):
        self._processor_configs: Dict[Any, Any] = {}
        self.line_processor_amount = AmountLineProcessor()
        self.line_processor_description = DescriptionLineProcessor()
        self.line_processor_date = DateLineProcessor()
        self.regex_line_processor_account_details = RegexLineProcessor(
            "account")
        # Few Generic initialisations
        self.line_processor_amount.set_start_regexes(
            PDF_STATEMENT_PROCESSOR.AMOUNT_LINE_START_REGEX)
        self.line_processor_date.set_start_regexes(
            PDF_STATEMENT_PROCESSOR.DATE_LINE_START_REGEX)

    @staticmethod
    def get_from_json(json_object: Dict[Any, Any], json_path: str) -> Any:
        '''Get the element from the json with path seperated by dots'''
        try:
            _json_paths = json_path.split('.')
            if len(_json_paths) == 1:
                return json_object[_json_paths[0]]
            _json_object = json_object[_json_paths[0]]
            if _json_object == []:
                return []
            return PDFStatementProcessor.get_from_json(_json_object, '.'.join(_json_paths[1:]))
        except KeyError:
            return []
        except TypeError:
            return []

    def load_config_for_processor(self, line_processor: RegexLineProcessor):
        '''Set the line processor config '''
        json_path = f"regex.{line_processor.get_processor_name()}"
        line_processor.set_start_regexes(
            PDFStatementProcessor.get_from_json(self._processor_configs,
                                                f"{json_path}.start"))
        line_processor.set_stop_regexes(
            PDFStatementProcessor.get_from_json(self._processor_configs,
                                                f"{json_path}.stop"))
        line_processor.set_match_regexes(
            PDFStatementProcessor.get_from_json(self._processor_configs,
                                                f"{json_path}.match"))
        line_processor.set_no_match_regexes(
            PDFStatementProcessor.get_from_json(self._processor_configs,
                                                f"{json_path}.no_match"))

    def load_config(self, json_config_file_name: str) -> None:
        '''Load the config from the file. The file format is as below
            the keys are regex processor names
            {
                "regex" : {
                    "amount" : {"start" : [],"stop" : [],"match" : [],"no_match" :[]},
                    "date" : {"start" : [],"stop" : [],"match" : [],"no_match" :[]},
                    "description" : {"start" : [],"stop" : [],"match" : [],"no_match" :[]},
                    "account" : {"start" : [],"stop" : [],"match" : [],"no_match" :[]},
                }
            }
            start, stop , match and no match needs to be regex strings for the correspoding
            actions
        '''
        json_file_full_path = PDFStatementProcessor.CONFIG_FOLDER/json_config_file_name
        if not json_file_full_path.exists():
            logging.error(
                "The given json config path %s do not exist!!", json_config_file_name)
            return
        try:
            self._processor_configs = load_json_file(
                json_file_full_path.open())
            # Initialise all the line processors
            self.load_config_for_processor(self.line_processor_amount)
            self.load_config_for_processor(self.line_processor_date)
            self.load_config_for_processor(self.line_processor_description)
            self.load_config_for_processor(
                self.regex_line_processor_account_details)
        except JSONDecodeError:
            pass

    @abstractmethod
    def process(self, queue_item: QueueItem) -> Tuple[bool, str, List[Transaction]]:
        '''Process the given request'''

    def get_transactions(self) -> List[Transaction]:
        '''Get the transactions list from the data'''
        transactions: List[Transaction] = []
        dates = self.line_processor_date.get_data_values()
        amounts = self.line_processor_amount.get_data_values()
        descriptions = self.line_processor_description.get_data_values()
        total_data_values = self.line_processor_description.get_total_data_values()
        # TODO: Add the transactions here
        transactions = [Transaction()
                        .description(cast(DescriptionValue,
                                          descriptions[x].get_value()).get_description())
                        .amount(cast(AmountValue,
                                     amounts[x].get_value()).get_amount())
                        .transaction_type(cast(AmountValue,
                                               amounts[x].get_value()).get_transaction_type())
                        .date(cast(DateValue,
                                   dates[x].get_value()).get_date())
                        for x in range(0, total_data_values)]

        # Uniquley identify the transaction based on statement file and line number
        # Since it wont be changes regardless of re-uploading
        return transactions

    def get_card_details(self) -> str:
        '''Get the collected credit card number'''
        if self.regex_line_processor_account_details.get_total_data_values() > 0:
            return cast(CardNumberValue, self.regex_line_processor_account_details.\
                get_data_values(
                )[-1].get_value()).get_card_number()
        return PDFStatementProcessor.CARD_NOT_FOUND

    def get_total_credits_debits(self) -> Tuple[Decimal, Decimal]:
        '''Get the total credits and debits made on the statement'''
        return self.get_total_credits_debits_for_values(self.line_processor_amount.
                                                        get_data_values())

    def get_total_credits_debits_for_values(self, values: List[DataValue])\
                                                 -> Tuple[Decimal, Decimal]:
        '''Get the total credits and debits made for the given list of Data Value'''
        _credits: Decimal = Decimal(0)
        _debits: Decimal = Decimal(0)
        for _value in values:
            value = cast(AmountValue, _value.get_value())
            if value.get_transaction_type() == TransactionType.CREDIT:
                _credits = _credits + value.get_amount()  #
            if value.get_transaction_type() == TransactionType.DEBIT:
                _debits = _debits + value.get_amount()

        return _credits, _debits
    

    # TODO: Remove these later
    def debug_values(self) -> None:
        for i in self.line_processor_date.get_data_values():
            print(DateValue.date_to_string(i.get_value().get_date()))
        for i in self.line_processor_description.get_data_values():
            print(i.get_value().get_description())
        for i in self.line_processor_amount.get_data_values():
            print(i.get_value().get_amount())
        print(self.line_processor_date.get_total_data_values())
        print(self.line_processor_description.get_total_data_values())
        print(self.line_processor_amount.get_total_data_values())