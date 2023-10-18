from enum import Enum
class TransactionType(Enum):
    CREDIT = 0
    DEBIT = 1

class AccountType(Enum):
    SAVINGS = 0
    CURRENT = 1
    CREDITCARD = 2
    
class Banks(Enum):
    HDFC = 0
    ICICI = 1
    KOTAK = 2
    SBI = 3
    HSBC = 4

class TransactionFileProcessingStatus(Enum):
    CREATED = 1
    PROCESSING = 2
    FAILED = 3
    PROCESSED = 5
    PROCESSED_PARTIAL = 6

class EnumUtil:
    '''
    If the given value is present in the given enum or the value itself is an Enum object and is the same
    as the given enum then the corresponding value is returned otherwise none
    Make sure enumBase is an Enum itself
    '''
    def valueToEnumText(value,enumBase):
        try:
            if isinstance(value,enumBase):
                return value.name
            if value in [x.name for x in enumBase]:
                return value
            return None
        except:
            return None
    
    '''
    If the given value is an Enum member or the name of an enum object
    Make sure enumBase is an enum itself
    '''
    def isEnumValue(value,enumBase):
        try:
            if isinstance(value,enumBase):
                return True
            if value in [x.name for x in enumBase]:
                return True
            return False
        except:
            return False
