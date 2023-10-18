from PersonalFinanceCLI.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
from PersonalFinanceCLI.models.transactions.AmountValue import AmountValue
from PersonalFinanceCLI.models.db.Enums import TransactionType
from decimal import Decimal

class AmountLineProcessor(RegexLineProcessor):
    def __init__(self):
        RegexLineProcessor.__init__(self)
        self.set_match_regexes(['([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9]'])
        #TODO Change "." not being present in the amount to no match regex
        self.SetFetchFunction(self.process_amount)
        pass

    def process_amount(self,line):
        try:
            lineVals = line.upper().replace(',','').split(' ')
            '''
            To seperate integers which may not be amounts
            For eg: Feature points may come along with amount but they will not have . decimals
            '''
            if "." not in lineVals[0]: 
                return None
            amountValue = AmountValue() \
                            .amount(Decimal(lineVals[0])) \
                            .txnType(TransactionType.DEBIT) \
                            .negativeEntry(False)
            if len(lineVals) > 1 and lineVals[1] == 'CR':
                amountValue.txnType(TransactionType.CREDIT)
            if amountValue.Getamount() < 0:
                amountValue.amount(0-amountValue.Getamount())
                amountValue.negativeEntry(True)
                if amountValue.GettxnType() == TransactionType.CREDIT:
                    amountValue.txnType(TransactionType.DEBIT)
                else: 
                    amountValue.txnType(TransactionType.CREDIT)
            return amountValue
        except:
            return None

