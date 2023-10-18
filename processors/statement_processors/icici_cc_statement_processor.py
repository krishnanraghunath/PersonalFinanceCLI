from PersonalFinanceCLI.processors.statement_processors.line_processors.amount_line_processor import AmountLineProcessor
from PersonalFinanceCLI.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
from PersonalFinanceCLI.processors.statement_processors.pdf_statement_processor import PDFStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.common import ICICI_CC_STATEMENT_PROCESSOR
from PersonalFinanceCLI.models.db.Enums import TransactionType


class ICICICCStatementProcessor(PDFStatementProcessor):
    def __init__(self,fileInfo,accountInfo):
        PDFStatementProcessor.__init__(self,fileInfo,accountInfo)
        '''
        For taking care of transactions being duplicated. Lucky we have this serial number
        '''
        self.serialNumberProcessor = RegexLineProcessor() 
        self.serialNumberProcessor.set_start_regexes(ICICI_CC_STATEMENT_PROCESSOR.SERIAL_LINE_START_REGEX)
        self.serialNumberProcessor.set_stop_regexes(ICICI_CC_STATEMENT_PROCESSOR.SERIAL_LINE_STOP_REGEX)
        self.serialNumberProcessor.set_match_regexes(ICICI_CC_STATEMENT_PROCESSOR.SERIAL_LINE_MATCH_REGEX)
        self.serialNumberProcessor.SetFetchFunction(ICICI_CC_STATEMENT_PROCESSOR.serial_number_fetch)
        self.serialNumberProcessor.initialise()

        self.statementAmountLineProcessor = AmountLineProcessor()
        self.statementAmountLineProcessor.set_start_regexes(ICICI_CC_STATEMENT_PROCESSOR.STATEMENT_AMOUNT_LINE_START_REGEX)
        self.statementAmountLineProcessor.set_stop_regexes(ICICI_CC_STATEMENT_PROCESSOR.STATEMENT_AMOUNT_LINE_STOP_REGEX)
        self.statementAmountLineProcessor.set_match_regexes(ICICI_CC_STATEMENT_PROCESSOR.STATEMENT_AMOUNT_LINE_MATCH_REGEX)
        self.statementAmountLineProcessor.SetPreProcessFunction(ICICI_CC_STATEMENT_PROCESSOR.statement_amount_pre_process)
        self.statementAmountLineProcessor.initialise()

        self.amountLineProcessor.set_start_regexes(ICICI_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_START_REGEX)
        self.amountLineProcessor.set_stop_regexes(ICICI_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_STOP_REGEX)
        self.amountLineProcessor.set_no_match_regexes(ICICI_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_NO_MATCH_REGEX)

        self.dateLineProcessor.set_start_regexes(ICICI_CC_STATEMENT_PROCESSOR.DATE_DESCRIPTION_LINE_START_REGEX)
        self.dateLineProcessor.set_stop_regexes(ICICI_CC_STATEMENT_PROCESSOR.DATE_DESCRIPTION_LINE_STOP_REGEX)

        self.descriptionLineProcessor.set_start_regexes(ICICI_CC_STATEMENT_PROCESSOR.DATE_DESCRIPTION_LINE_START_REGEX)
        self.descriptionLineProcessor.set_stop_regexes(ICICI_CC_STATEMENT_PROCESSOR.DATE_DESCRIPTION_LINE_STOP_REGEX)
        self.descriptionLineProcessor.set_no_match_regexes(ICICI_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_NOT_MATCH_REGEX)

        self.accountDetailsProcessor.set_start_regexes(ICICI_CC_STATEMENT_PROCESSOR.DATE_DESCRIPTION_LINE_START_REGEX)
        self.accountDetailsProcessor.set_stop_regexes(ICICI_CC_STATEMENT_PROCESSOR.DATE_DESCRIPTION_LINE_STOP_REGEX)
        self.accountDetailsProcessor.set_match_regexes(ICICI_CC_STATEMENT_PROCESSOR.ACCOUNT_NUMBER_LINE_MATCH_REGEX)
        self.accountDetailsProcessor.SetFetchFunction(ICICI_CC_STATEMENT_PROCESSOR.process_card_number)
        

    '''
    Remove the current transactions of duplcates based on serial 
    '''
    def remove_duplicate_entries(self):
        serial_numbers_value = list(map(lambda x:x.Getvalue(),self.serialNumberProcessor.GetValues()))
        index_to_remove = []
        serial_numbers = []
        for valueIndex in range(self.serialNumberProcessor.GetTotalValues()):
            if serial_numbers_value[valueIndex] in serial_numbers:
                index_to_remove.append(valueIndex)
            else:
                serial_numbers.append(serial_numbers_value[valueIndex])
        '''
        remove the item and each time the indices of all the subsequent elements will get decremenetd by 1
        '''
        removed_indices = 0
        for i in index_to_remove:
            self.amountLineProcessor.remove(i - removed_indices)
            self.dateLineProcessor.remove(i - removed_indices)
            self.descriptionLineProcessor.remove(i - removed_indices)
            self.serialNumberProcessor.remove(i - removed_indices)
            removed_indices = removed_indices + 1

    def process(self):
        for line in self.lines.splitlines():
            self.amountLineProcessor.process(line)
            self.dateLineProcessor.process(line)
            self.descriptionLineProcessor.process(line)
            self.accountDetailsProcessor.process(line)
            self.statementAmountLineProcessor.process(line)
            self.serialNumberProcessor.process(line)

        #Checking we have right data to proceed    
        if  self.dateLineProcessor.GetTotalValues()!=  self.descriptionLineProcessor.GetTotalValues() or \
            self.amountLineProcessor.GetTotalValues()!=  self.dateLineProcessor.GetTotalValues() or \
            self.serialNumberProcessor.GetTotalValues() != self.amountLineProcessor.GetTotalValues() or \
            self.statementAmountLineProcessor.GetTotalValues() != 5 or \
            self.accountDetailsProcessor.GetTotalValues() == 0:
            print(self.dateLineProcessor.GetTotalValues())
            print(self.descriptionLineProcessor.GetTotalValues())
            for i in self.descriptionLineProcessor.GetValues():
                print(i.Getvalue().Getdescription())
            print(self.amountLineProcessor.GetTotalValues())
            print(self.serialNumberProcessor.GetTotalValues())
            print(self.statementAmountLineProcessor.GetTotalValues())
            print(self.accountDetailsProcessor.GetTotalValues())
            print("Unable to findout required data. Debug with the said statement")
            return False,[]
        #Checking we are using the statement belonging to the account itself  
        if not self.verify_account_details():
            return False,[]
        
        #In some special case the transactions recorded seems to be getting repeated. 
        #Taking care of such situation
        self.remove_duplicate_entries()

        #Checking the statement section 
        statementAmounts = self.statementAmountLineProcessor.GetValues()
        totalDue = statementAmounts[0].Getvalue().Getamount()
        previousDue = statementAmounts[1].Getvalue().Getamount()
        totalExpenditures = statementAmounts[2].Getvalue().Getamount()
        totalCash = statementAmounts[3].Getvalue().Getamount()
        totalPayments = statementAmounts[4].Getvalue().Getamount()
        #If Previous Due is CR, means a positive due, same is applicable for Total Due
        if statementAmounts[1].Getvalue().GettxnType() == TransactionType.CREDIT:
            previousDue = 0 - previousDue
        if statementAmounts[0].Getvalue().GettxnType() == TransactionType.CREDIT:
            totalDue = 0 - totalDue
        #Final cros verification of values collected
        if totalDue != (previousDue + totalExpenditures + totalCash - totalPayments):
            print("Unable to match amounts in statements. Debug with the said statement")
            return False,[]
        #Now that we can use totalExpenditures and totalPayments to verify Transaction Section
        
        #Cross checking statement amounts and parsed transaction amounts/details
        totalPaymentsCalculated,totalExpendituresCalculated = self.get_total_credits_debits()
        if totalPayments!=totalPaymentsCalculated or \
            totalExpenditures!=totalExpendituresCalculated:
            print("Unable to match statement summary amount and calculated amounts from Parsed data. Debug with the said file")
            return False,[]
        return True,self.create_transaction_table()
    
       