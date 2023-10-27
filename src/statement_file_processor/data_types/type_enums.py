'''All the Enum realted classes and function'''
from typing import Type, Optional, Union
from enum import Enum

class TransactionType(Enum):
    '''Transaction types denoting the type of transaction Credit or Debit'''
    CREDIT = 0
    DEBIT = 1



class AccountType(Enum):
    '''Account Type: Currently Savings/Current and Credit Card'''
    SAVINGS = 0
    CURRENT = 1
    CREDITCARD = 2


class Banks(Enum):
    '''Currently supported banks'''
    HDFC = 0
    ICICI = 1
    KOTAK = 2
    SBI = 3
    HSBC = 4


class TransactionFileProcessingStatus(Enum):
    '''The status of the transaction file processing'''
    CREATED = 1
    PROCESSING = 2
    FAILED = 3
    PROCESSED = 5
    PROCESSED_PARTIAL = 6


class EnumUtil:
    '''Util class for Enums'''

    @staticmethod
    def convert_enum_value_to_text(value: Union[str, Enum],
                                    enum_base_class: Type[Enum]) -> Optional[str]:
        ''' If the given value is present in the given enum or the value itself 
        is an Enum  object and is the same as the given enum then the corresponding 
        value is returned otherwise none Make sure enumBase is an Enum itself'''
        if isinstance(value, enum_base_class):
            return value.name
        if value in [x.name for x in enum_base_class]:
            return value
        return None

    @staticmethod
    def is_enum_value(value: Union[str, Enum], enum_base_class: Type[Enum]) -> bool:
        '''
        If the given value is an Enum member or the name of an enum object
        Make sure enumBase is an enum itself
        '''
        if isinstance(value, enum_base_class):
            return True
        if value in [x.name for x in enum_base_class]:
            return True
        return False
