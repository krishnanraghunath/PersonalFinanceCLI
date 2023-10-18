from PersonalFinanceCLI.processors.statement_processors.pdf_statement_processor import PDFStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.common  import KOTAK_CC_STATEMENT_PROCESSOR
from PersonalFinanceCLI.models.db.Enums import TransactionType
from functools import reduce


class KotakCCStatementProcessor(PDFStatementProcessor):
    IGNORE_PAYMENTS_ENTRY = [
        'PAYMENT RECEIVED-MOBILE FUNDS TRANSFER',
        'PAYMENT RECEIVED-NEFT',
        'PAYMENT RECEIVED-KOTAK IMPS'
    ]
    ANNUAL_STATEMENT_DESCS = [
        'GST',
        'ANNUAL FEE'
    ]
    DescriptionNoMatchRegex = lambda x:x not in KotakCCStatementProcessor.IGNORE_PAYMENTS_ENTRY

    def __init__(self,fileInfo,accountInfo):
        PDFStatementProcessor.__init__(self,fileInfo,accountInfo)
        self.amountLineProcessor.set_start_regexes(KOTAK_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_START_REGEX)
        self.amountLineProcessor.set_stop_regexes(KOTAK_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_STOP_REGEX)
        self.amountLineProcessor.set_match_regexes(KOTAK_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_MATCH_REGEX)
        self.descriptionLineProcessor.set_start_regexes(KOTAK_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_START_REGEX)
        self.descriptionLineProcessor.set_stop_regexes(KOTAK_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_STOP_REGEX)
        self.descriptionLineProcessor.set_no_match_regexes(KOTAK_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_NO_MATCH_REGEX)
        self.dateLineProcessor.set_start_regexes(KOTAK_CC_STATEMENT_PROCESSOR.DATE_LINE_START_REGEX)
        self.dateLineProcessor.set_stop_regexes(KOTAK_CC_STATEMENT_PROCESSOR.DATE_LINE_STOP_REGEX)
        self.accountDetailsProcessor.set_start_regexes( KOTAK_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_START_REGEX )
        self.accountDetailsProcessor.set_stop_regexes(KOTAK_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_STOP_REGEX)
        self.accountDetailsProcessor.set_match_regexes(KOTAK_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_MATCH_REGEX)
        self.accountDetailsProcessor.SetFetchFunction(KOTAK_CC_STATEMENT_PROCESSOR.process_card_number)
        self.amountLineProcessor.initialise()
        self.descriptionLineProcessor.initialise()
        self.dateLineProcessor.initialise()

    
    '''
    Finding current months debits and credits other than NEFT or Payments to match up the due amount. This is specific for
    Kotak Credit Card only!!
    '''
    def get_calculated_dues_from_transactions(self,transactions):
        filter_transactions = lambda y:y.Getdesc() not in KotakCCStatementProcessor.IGNORE_PAYMENTS_ENTRY
        map_amount = lambda y:y.Getamount() if y.GettxnType() == TransactionType.CREDIT else 0-y.Getamount()
        return 0-reduce(lambda x,y:x+y,map(lambda z:map_amount(z),filter(lambda w:filter_transactions(w),transactions)))
  

    def process(self):
        for line in self.lines.splitlines():
            self.amountLineProcessor.process(line)
            self.descriptionLineProcessor.process(line)
            self.dateLineProcessor.process(line)
            self.accountDetailsProcessor.process(line)

        #Cross verifying account number details
        skip_account_verification_check = False
        #For annual fees statement the card details may not be present.
        if self.accountDetailsProcessor.GetTotalValues() == 0:
            print("Unable to get card details.Checking if Annual statement")
            if len(list(filter(lambda x:x.Getvalue().Getdescription() not in KotakCCStatementProcessor.ANNUAL_STATEMENT_DESCS,
                          self.descriptionLineProcessor.GetValues()))) == 0:
                print("Looks like an annual statement!!.Skipping Account number validation")    
                skip_account_verification_check = True 
        if not skip_account_verification_check:
             if not self.verify_account_details():
                return False,[]
        
    
        #Dates count and descriptions count should be same
        #Amount should have an extra value for subtotal
        if self.dateLineProcessor.GetTotalValues() != \
            self.descriptionLineProcessor.GetTotalValues() or \
            self.dateLineProcessor.GetTotalValues() != \
            self.amountLineProcessor.GetTotalValues() - 1:
            return False,[]

        #Creating the transaction entries 
        transactions = self.create_transaction_table()

        #Cross verifying calculated Dues and Dues as per Statement
        totalDueAsPerStatement = self.amountLineProcessor.GetValues()[-1].Getvalue().Getamount()
        totalCalculatedDue = self.get_calculated_dues_from_transactions(transactions)
        if totalCalculatedDue != totalDueAsPerStatement:
            print("Unable to match Due amount with that of calculated one from captured transaction")
            return False,[]
        
        return True,transactions
        
