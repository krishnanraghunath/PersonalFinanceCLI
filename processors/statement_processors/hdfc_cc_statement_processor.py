# from datetime import date
from PersonalFinanceCLI.processors.statement_processors.line_processors.amount_line_processor import AmountLineProcessor
from PersonalFinanceCLI.processors.statement_processors.pdf_statement_processor import PDFStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.common import HDFC_CC_STATEMENT_PROCESSOR
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.db.Enums import TransactionType

from decimal import Decimal
from functools import reduce



class HDFCCCStatementProcessor(PDFStatementProcessor):
    HDFC_DUE_ERROR_THRESHOLD = 50
    HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD = 25
    def __init__(self,fileInfo,accountInfo):
        PDFStatementProcessor.__init__(self,fileInfo,accountInfo)
        self.statementAmountLineProcessor = AmountLineProcessor()
        self.amountLineProcessor.set_start_regexes(HDFC_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_START_REGEX)
        self.amountLineProcessor.set_stop_regexes(HDFC_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_STOP_REGEX)
        self.statementAmountLineProcessor.set_start_regexes(HDFC_CC_STATEMENT_PROCESSOR.STATEMENT_AMOUNT_LINE_START_REGEX)
        self.statementAmountLineProcessor.set_stop_regexes(HDFC_CC_STATEMENT_PROCESSOR.STATEMENT_AMOUNT_LINE_STOP_REGEX)
        self.descriptionLineProcessor.set_start_regexes(HDFC_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_START_REGEX)
        self.descriptionLineProcessor.set_stop_regexes(HDFC_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_STOP_REGEX)
        self.descriptionLineProcessor.set_no_match_regexes(HDFC_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_NO_MATCH_REGEX)
        self.dateLineProcessor.set_stop_regexes(HDFC_CC_STATEMENT_PROCESSOR.DATE_LINE_STOP_REGEX)
        self.accountDetailsProcessor.set_start_regexes(HDFC_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_START_REGEX)
        self.accountDetailsProcessor.set_stop_regexes(HDFC_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_STOP_REGEX)
        self.accountDetailsProcessor.set_match_regexes(HDFC_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_MATCH_REGEX)
        self.accountDetailsProcessor.SetFetchFunction(HDFC_CC_STATEMENT_PROCESSOR.process_card_number)
        self.statementAmountLineProcessor.initialise()
    
    def search_for_descriptions_between_date_amount_blurbs(self,blurbIndex):
        dateBlobs = self.dateLineProcessor.blurbs()
        amountBlobs = self.amountLineProcessor.blurbs()
        try:
            description_search_start = dateBlobs[blurbIndex].GetendLine()
            description_search_end = amountBlobs[blurbIndex].GetstartLine()
            self.descriptionLineProcessor.SetLineCounter(description_search_start)
            self.descriptionLineProcessor.OverrideAndProcess(
                self.lines.splitlines()[
                        description_search_start: 
                        description_search_end
                        ]) 
            self.descriptionLineProcessor.re_organize()
        except:
            #If blurbIndex > len(amounts or date blurbs)
            pass 


    def getCalculatedAmounts(self):
        amounts = self.amountLineProcessor.GetValues()
        count = self.amountLineProcessor.GetTotalValues()
        get_amount_if_txn_matches_func = lambda x,y: \
                                amounts[x].Getvalue().Getamount() \
                                if amounts[x].Getvalue().GettxnType() == y \
                                else Decimal(0)
        get_amount_if_txn_matches_and_negativeEntry_func = lambda x,y: \
                                amounts[x].Getvalue().Getamount() \
                                if amounts[x].Getvalue().GettxnType() == y \
                                      and amounts[x].Getvalue().GetnegativeEntry()\
                                else Decimal(0)
        
        reduce_function = lambda f,c: reduce(lambda x,y: x+y, \
                                                map(lambda z:
                                                    f(z,c),\
                                                    range(0,count)))
        
        #Summing up all the transactions marked as CREDIT
        total_credit = reduce_function(get_amount_if_txn_matches_func,TransactionType.CREDIT) 
        #Summing up all the transactions marked as DEBIT
        total_debit = reduce_function(get_amount_if_txn_matches_func,TransactionType.DEBIT) 
        #Summing up all the transactions marked as DEBIT with NegativeEntry flag on
        wrongly_credited = reduce_function(get_amount_if_txn_matches_and_negativeEntry_func,
                                            TransactionType.DEBIT) 
        #Summing up all the transactions marked as CREDIT with NegativeEntry flag on
        wrongly_debited = reduce_function(get_amount_if_txn_matches_and_negativeEntry_func,
                                        TransactionType.CREDIT)  
        return (wrongly_credited,wrongly_debited,total_credit,total_debit)
    


    def process(self):
        transactions = []
        for line in self.lines.splitlines():
            self.amountLineProcessor.process(line)
            self.descriptionLineProcessor.process(line)
            self.dateLineProcessor.process(line)
            self.statementAmountLineProcessor.process(line)
            self.accountDetailsProcessor.process(line)
        statementAmounts = self.statementAmountLineProcessor.GetValues()
        #Cross verifying the Credit card number
        if not self.verify_account_details():
            return False,[]
        
        if self.statementAmountLineProcessor.GetTotalValues() != 5:
            print("Error in getting proper statement values")
            return False,[]

        #Get the statement summary values
        openingBalance = statementAmounts[0].Getvalue().Getamount()
        payments = statementAmounts[1].Getvalue().Getamount()
        debits = statementAmounts[2].Getvalue().Getamount()
        finance = statementAmounts[3].Getvalue().Getamount()
        totalDues = statementAmounts[4].Getvalue().Getamount()
        #TODO: Elaborate why
        if statementAmounts[4].Getvalue().GetnegativeEntry():
            totalDues = 0 - totalDues
        if statementAmounts[0].Getvalue().GetnegativeEntry(): 
            openingBalance = 0 - openingBalance
        #Observed an error with error credit 
        hdfcBankErrorCredit,hdfcBankErrorDebit,paymentsCal,debitsCal = self.getCalculatedAmounts()
        errorDiff = openingBalance - payments + debits + finance + hdfcBankErrorDebit - hdfcBankErrorCredit - totalDues
        extra_payments_or_debits = 0
        #See if the calculated payments to be made based on cash flow and the as rquested by the statement is within
        # the given threshold
        if abs(payments-paymentsCal) < HDFCCCStatementProcessor.HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD:
            if abs(payments-paymentsCal) != 0:
                extra_payments_or_debits = extra_payments_or_debits + payments - paymentsCal
        else:
            print("Mismatch in collected summary of statements and summary")
            return False,[]
        
        if abs(debits-debitsCal + finance) < HDFCCCStatementProcessor.HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD:
            if abs( debits-debitsCal + finance) != 0:
                extra_payments_or_debits = extra_payments_or_debits - ( debits - debitsCal + finance )
        else:
            if abs( debits - debitsCal ) < HDFCCCStatementProcessor.HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD:
                if abs(debits-debitsCal) != 0:
                    extra_payments_or_debits = extra_payments_or_debits - (debits-debitsCal)
            else:
                print("Mismatch in collected summary of statements and summary")
                return False,[]

        if abs(errorDiff) > HDFCCCStatementProcessor.HDFC_DUE_ERROR_THRESHOLD:
            if abs(abs(errorDiff) - finance) > HDFCCCStatementProcessor.HDFC_DUE_ERROR_THRESHOLD:
                print("Mismatch in collected summary of payments -> %d" %errorDiff)
                return False,[]

        # totalValueCalculated = self.getTotalCashFlowFromStatementTransactions( amounts,self.amountLineProcessor.GetTotalValues())
    
        if  self.dateLineProcessor.GetTotalValues() !=  \
            self.amountLineProcessor.GetTotalValues():
            print("Failed to get all entries.Mismatch in Dates and Amounts")

        #Handling an edge case where the description comes in between last date and amout entries
        if  self.descriptionLineProcessor.GetTotalValues() < \
            self.amountLineProcessor.GetTotalValues():
            #Case -> A section of description got skipped between the  last blurbs of amounts & dates 
            self.search_for_descriptions_between_date_amount_blurbs(-1)
            #Case -> A section of description got skipped between the  second last blurbs of amounts & dates 
            self.search_for_descriptions_between_date_amount_blurbs(-2)
            #Havent found a 3rd last yet. 

        if  self.descriptionLineProcessor.GetTotalValues() != \
            self.amountLineProcessor.GetTotalValues():
            print("Mismatch in Description and Amounts")
            return False,transactions

        currentTransactions = self.create_transaction_table()
        #Add an extra Entry Credit/Debit to adjust small difference under threshold (Not the issue with
        # programme but with the statement itself)
        if abs(extra_payments_or_debits) > 0:
            extraTxn = TransactionCollectionModel() \
                            .src(self.accountInfo.GetaccountNumber()) \
                            .dest("EXTERNAL") \
                            .desc("ADJUST_PAYMENTS_DATA") \
                            .amount(Decimal(abs(extra_payments_or_debits))) \
                            .txnType(TransactionType.CREDIT) \
                            .date(self.dateLineProcessor.GetValues()[-1].Getvalue().Getdate()) \
                            .txnId("%s%d"%(self.fileInfo.GetfileKey(),-1))
            
            if extra_payments_or_debits < 0:
                extraTxn.txnType(TransactionType.DEBIT)
            currentTransactions.append(extraTxn)
        return True,currentTransactions
