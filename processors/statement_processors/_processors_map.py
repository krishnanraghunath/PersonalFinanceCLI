from PersonalFinanceCLI.processors.statement_processors.hdfc_cc_statement_processor import HDFCCCStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.icici_cc_statement_processor import ICICICCStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.kotak_cc_statement_processor import KotakCCStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.hsbc_cc_statement_processor import HSBCCCStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.hdfc_bankaccount_statement_processor import HDFCBankAccountStatementProcessor

ProcessorsMapping = {
    'HDFC:CREDITCARD:application/pdf' : HDFCCCStatementProcessor,
    'KOTAK:CREDITCARD:application/pdf' : KotakCCStatementProcessor,
    'ICICI:CREDITCARD:application/pdf' : ICICICCStatementProcessor,
    'HSBC:CREDITCARD:application/pdf' : HSBCCCStatementProcessor,
    'HDFC:SAVINGS:application/txt'    : HDFCBankAccountStatementProcessor,
    'HDFC:CURRENT:application/txt'    : HDFCBankAccountStatementProcessor,
    'HDFC:SAVINGS:application/csv' : HDFCBankAccountStatementProcessor,
    'HDFC:CURRENT:application/csv' : HDFCBankAccountStatementProcessor
}