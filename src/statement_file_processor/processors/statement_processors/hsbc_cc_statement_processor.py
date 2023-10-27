# from datetime import date
from PersonalFinanceCLI.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
from PersonalFinanceCLI.processors.statement_processors.line_processors.amount_line_processor import AmountLineProcessor
from PersonalFinanceCLI.processors.statement_processors.pdf_statement_processor import PDFStatementProcessor
from PersonalFinanceCLI.processors.statement_processors.common import HSBC_CC_STATEMENT_PROCESSOR
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.db.Enums import TransactionType
from re import compile
from decimal import Decimal
from functools import reduce


'''
Supporting Data Classes for Loan Processing
'''


class HSBCCCStatementProcessor(PDFStatementProcessor):
    HDFC_PURCHASE_ERROR_THRESHOLD_WITH_LOANS = 1
    HDFC_PAYMENTS_DEBITS_ERROR_THRESHOLD = 25
    def __init__(self,fileInfo,accountInfo):
        PDFStatementProcessor.__init__(self,fileInfo,accountInfo)
        self.statement_year = None
        self.statementAmountLineProcessor = AmountLineProcessor()
        self.amountLineProcessor.set_start_regexes(HSBC_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_START_REGEX)
        self.amountLineProcessor.set_stop_regexes(HSBC_CC_STATEMENT_PROCESSOR.AMOUNT_LINE_STOP_REGEX)
        self.statementAmountLineProcessor.set_start_regexes(HSBC_CC_STATEMENT_PROCESSOR.STATEMENT_AMOUNT_LINE_START_REGEX)
        self.statementAmountLineProcessor.set_stop_regexes(HSBC_CC_STATEMENT_PROCESSOR.STATEMENT_AMOUNT_LINE_STOP_REGEX)
        self.descriptionLineProcessor.set_start_regexes(HSBC_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_START_REGEX)
        self.descriptionLineProcessor.set_stop_regexes(HSBC_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_STOP_REGEX)
        self.descriptionLineProcessor.set_no_match_regexes(HSBC_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_NOT_MATCH_REGEX)
        self.dateLineProcessor.set_start_regexes(HSBC_CC_STATEMENT_PROCESSOR.DATE_LINE_START_REGEX)
        self.dateLineProcessor.set_stop_regexes(HSBC_CC_STATEMENT_PROCESSOR.DATE_LINE_STOP_REGEX)
        self.dateLineProcessor.set_match_regexes(HSBC_CC_STATEMENT_PROCESSOR.DATE_LINE_MATCH_REGEX)   
  
        
        # self.accountDetailsProcessor.set_start_regexes(HDFC_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_START_REGEX)
        # self.accountDetailsProcessor.set_stop_regexes(HDFC_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_STOP_REGEX)
        # self.accountDetailsProcessor.set_match_regexes(HDFC_CC_STATEMENT_PROCESSOR.ACCOUNT_DETAILS_LINE_MATCH_REGEX)
        # self.accountDetailsProcessor.SetFetchFunction(HDFC_CC_STATEMENT_PROCESSOR.process_card_number)

        self.statementAmountLineProcessor.initialise()

        self.descriptionLineOverflowProcessor =  RegexLineProcessor()
        self.descriptionLineOverflowProcessor.set_match_regexes(HSBC_CC_STATEMENT_PROCESSOR.DESCRIPTION_LINE_OVER_FLOW_MATCH_REGEX)
        self.descriptionLineOverflowProcessor.SetFetchFunction(lambda x:x)
        self.statementPeriodProcessor =  RegexLineProcessor()
        self.statementPeriodProcessor.set_match_regexes(HSBC_CC_STATEMENT_PROCESSOR.STATEMENT_PERIOD_MATCH_REGEX)
        self.statementPeriodProcessor.SetFetchFunction(lambda x:HSBC_CC_STATEMENT_PROCESSOR.process_statement_year(x))

    '''
    Few transactions will be deleted/modified in order to nullify the lack of information regarding loans in statements.
    Basics
    (Loan Principal + Loan Interst)/Term -> Monthly EMI
    But this Loan Interest amount is hidden and we need to find it out from emi*terms - principal
    Current Transactions for a Loan Taken with say MARS Corp
    Statement Month -> 0 (Principal:2000, Interest 400)

    --> MARS Corp 2000.00
    --> MARS Corp 2000.00 CR
    --> MARS Corp 1ST OF 6 INSTALLMENTS 400.00
    --> MARS Corp 1ST OF 6 INSTALLMENTS 400.00CR

    Statment Month n
    --> MARS Corp nth OF 6 INSTALLMENTS 400.00
    --> MARS Corp nth OF 6 INSTALLMENTS 400.00CR

    So here basically wed ont have a seperate line item for Interest and effectively the emi and CR amount will nullify each other 
    in each statement. So we would have to work it our in a more realistic approach
    Eg:
    --> MARS Corp 2000.00 
    --> MARS Corp (Principal:2000.00,Interest:400) 400.00 
    --> MARS Corp 1st of 6 Installments 400.00 CR

    Statment Month n
    --> MARS Corp nth OF 6 INSTALLMENTS 400.00 CR
     ==> PT.2 ==> if there are mulitple loans with same description line as in RELIANCE 100, RELIANCE 200, we are not 
     diving deep into those and categorise them absed on amounts and all. We would accumalate them as a single loan . 
     But if we are multiple loans with different description line we will seperate them
    '''


    def restructure_loans(self,loan_line_item_descriptions):
        auto_adjusted_transactions = self.get_auto_adjust_transactons()
        loans = {}
        indices_to_delete = []
        for loan_line_item_description in loan_line_item_descriptions:
            #TODO: Convert these to BaseModel based implementation
            loans[loan_line_item_description] = {
                "principal" : 0,
                "principal_and_interest" : 0,
                "interest" : 0
            }
            for auto_adjusted_transaction_description in auto_adjusted_transactions:
                if auto_adjusted_transaction_description.startswith(loan_line_item_description):
                    auto_adjusted_transaction = auto_adjusted_transactions[auto_adjusted_transaction_description]
                    indices = auto_adjusted_transaction["indices"]
                    if not auto_adjusted_transaction["installment"]:
                        '''If not an install it would be the linke corresponding 
                        to the total loan amount.(The accumalating operation may not be necessary. SEE PT.2 in above)'''
                        loans[loan_line_item_description]["principal"]  =  \
                                            loans[loan_line_item_description]["principal"]  \
                                            + auto_adjusted_transaction["amount"]
                        '''Remove Loan lines where transaction type is not credit'''
                        for index in indices:
                            if self.amountLineProcessor.GetValues()[index].Getvalue().GettxnType() == TransactionType.CREDIT:
                                indices_to_delete.append(index)
                        continue
                    else:
                        '''If the installment is 1st of many, then take the loan amount. 
                        (The accumalating operation may not be necessary SEE PT.2 in above)'''
                        if auto_adjusted_transaction["serial"] == 1:
                            loans[loan_line_item_description]["principal_and_interest"]  = \
                            loans[loan_line_item_description]["principal_and_interest"] + \
                            auto_adjusted_transaction["loan"]
                        for index in indices:
                            if self.amountLineProcessor.GetValues()[index].Getvalue().GettxnType() == TransactionType.DEBIT:
                                indices_to_delete.append(index)
       
        for loan in loans:
            loans[loan]["interest"] = loans[loan]["principal_and_interest"] - loans[loan]["principal"]
        self.amountLineProcessor.removeAll(indices_to_delete)
        self.descriptionLineProcessor.removeAll(indices_to_delete)
        self.dateLineProcessor.removeAll(indices_to_delete)
        return loans
 


        
    def sanitise_usd_values(self):
        deleted_entries = 0
        '''Check for existance of USD (US Dollar transactions) in lines'''
        for descriptionIndex in range(self.descriptionLineProcessor.GetTotalValues()):
            descriptionIndex = descriptionIndex - deleted_entries
            if self.descriptionLineProcessor.GetValues()[descriptionIndex].Getvalue().Getdescription() == 'USD':
                line_number = self.descriptionLineProcessor.GetValues()[descriptionIndex].Getline()
                self.descriptionLineProcessor.remove(descriptionIndex)
                deleted_entries = deleted_entries + 1
                for amountIndex in range(self.amountLineProcessor.GetTotalValues()):
                    amount_line_number = self.amountLineProcessor.GetValues()[amountIndex].Getline()
                    '''If the amount happens to be coming 2 lines after USD remove it as well'''
                    if amount_line_number ==  line_number + 2:
                        self.amountLineProcessor.remove(amountIndex)
                        break
    
    
    '''Will look for DEBIT and CREDIT tranasction so fsame amount with same description'''
    def get_auto_adjust_transactons(self):
        auto_adjust_amounts = {}
        amounts = self.amountLineProcessor.GetValues()
        descs = self.descriptionLineProcessor.GetValues()
        for index in range(self.amountLineProcessor.GetTotalValues()):
            amount = amounts[index].Getvalue().GetActualAmount()
            desc = descs[index].Getvalue().Getdescription()
            if desc not in auto_adjust_amounts:
                #TODO: Convert these to BaseModel based implementation
                auto_adjust_amounts[desc] = {  "amount":-1,"total":0,"count":0,"indices":[],"desc":desc,"installment":False}
            if auto_adjust_amounts[desc]["amount"] == -1:
                auto_adjust_amounts[desc]["amount"] = abs(amount)
            auto_adjust_amounts[desc]["loan"] = abs(amount)
            auto_adjust_amounts[desc]["total"] = auto_adjust_amounts[desc]["total"] + amount 
            auto_adjust_amounts[desc]["count"] = auto_adjust_amounts[desc]["count"] + 1
            auto_adjust_amounts[desc]["indices"].append(index)
            installments = compile("(\d)\w{2}\s*OF\s*(\d)\s*INSTALLMENTS$").search(desc)
            if installments:
                installments = installments.groups()
                auto_adjust_amounts[desc]["installment"] = True
                auto_adjust_amounts[desc]["term"] = int(installments[1])
                auto_adjust_amounts[desc]["serial"] = int(installments[0])  
                auto_adjust_amounts[desc]["loan"] = int(installments[1])*abs(amount)      
        return {x["desc"]:x for x in list(filter(lambda x:x["count"] == 2 and x["total"] == 0,auto_adjust_amounts.values()))}

   
    def process(self):
        loan_line_item_descriptions = []
        transactions = []
        self.descriptionLineOverflowProcessor.OverrideAndProcess(self.lines.splitlines())
        self.statementPeriodProcessor.OverrideAndProcess(self.lines.splitlines())
        if self.statementPeriodProcessor.GetTotalValues() == 0:
            print("Unable to fetch Statement Year from PDF.")
            return False,[]
        self.statement_year = self.statementPeriodProcessor.GetValues()[0].Getvalue()
        self.dateLineProcessor.SetPreProcessFunction(HSBC_CC_STATEMENT_PROCESSOR.pre_process_date_function(self.statement_year)) 
        for line in self.lines.splitlines():
            # print("%s -> %s"%(self.dateLineProcessor._processing,line))
            self.amountLineProcessor.process(line)
            self.descriptionLineProcessor.process(line)
            self.dateLineProcessor.process(line)
            self.statementAmountLineProcessor.process(line)
            # self.accountDetailsProcessor.process(line)
        
        '''For international Transactions USD fields would be present. Getting Rid of them'''
        self.sanitise_usd_values()
        '''
        Following is for combining overflowed line 
        '''
        for overFlowedline in self.descriptionLineOverflowProcessor.GetValues():
            for description in self.descriptionLineProcessor.GetValues():
                #Combining the 2 subsequent line with the last line of the two being an overflowed line
                if overFlowedline.Getline() - description.Getline() == 1:
                    #To be later used to identify transactions to be deleted
                    loan_line_item_descriptions.append(description.Getvalue().Getdescription())
                    description.Getvalue().description(
                        "%s %s"%(description.Getvalue().Getdescription() , overFlowedline.Getvalue()))
        loan_line_item_descriptions = list(set(loan_line_item_descriptions))
                    

        '''Verification 0: Len verification'''
        if self.descriptionLineProcessor.GetTotalValues() + 1 != (self.dateLineProcessor.GetTotalValues()):
            #Len(dates) would be +1 compared to descriptions , the last one being Date corresponding to Net due
            print("Length of Descriptions and Dates do not match as expcted.len(Dates) = len(Descriptions) + 1")
            return False,[]
        #Now remove the last date which is corresponding Net Due, the non transactional date
        self.dateLineProcessor.slice(None,-1)

        if self.amountLineProcessor.GetTotalValues() !=  (self.descriptionLineProcessor.GetTotalValues() + 6):
            print("Amounts Length is not as expected (description length + 6 )")
            return False,[]

        '''
        We expect Len(amounts) = Len(descriptions) + 6
        6 being 
        Index 0 -> Opening Balance
        Index[-5:] => 
            a) TOTAL PURCHASE OUTSTANDING
            b) TOTAL CASH OUTSTANDING
            c) TOTAL BALANCE TRANSFER OUTSTANDING
            d) TOTAL LOAN OUTSTANDING
            e) NET OUTSTANDING BALANCE
        Verify sum(a->d) = e
        '''
        amounts = self.amountLineProcessor.GetValues()
        opening_balance_from_transactions_summary = amounts[0].Getvalue().GetActualAmount()
        total_purchase_outstanding = amounts[-5].Getvalue().GetActualAmount()
        total_cash_outstanding = amounts[-4].Getvalue().GetActualAmount()
        total_balace_transfer_outstanding = amounts[-3].Getvalue().GetActualAmount()
        total_load_outstanding = amounts[-2].Getvalue().GetActualAmount()
        net_outstanding_balance = amounts[-1].Getvalue().GetActualAmount()
        net_outstanding_balance = amounts[-1].Getvalue().GetActualAmount()

        if (total_purchase_outstanding + total_cash_outstanding + 
            total_balace_transfer_outstanding + total_load_outstanding) != \
            net_outstanding_balance:
            return False,[]
        '''Removing the first one(opening balance) and last 5 (all the non transactional values)'''
        self.amountLineProcessor.slice(1,-5)
        '''With multiple pages we will have multiple instances of  statement summaries'''
        if self.statementAmountLineProcessor.GetTotalValues() < 4:
            print("Failed to collect all the statement summary amounts.")
            return False,[]
        
        self.statementAmountLineProcessor.slice(None,4)
        statement_amounts = self.statementAmountLineProcessor.GetValues()
        opening_balance_from_statement_summary = statement_amounts[0].Getvalue().GetActualAmount()
        purchases_from_statement_summary = statement_amounts[1].Getvalue().GetActualAmount()
        payments_from_statement_summary = statement_amounts[2].Getvalue().GetActualAmount()
        totalDue_from_statement_summary = statement_amounts[3].Getvalue().GetActualAmount()
        if(opening_balance_from_statement_summary + purchases_from_statement_summary - payments_from_statement_summary) \
              != totalDue_from_statement_summary:
            print("Unable to find proper statement summary/statement summary is not matching")
            return False,[]
        if opening_balance_from_transactions_summary != opening_balance_from_statement_summary:
            print("Opening Balances fetched from PDF not matching. Not proceeding as parsed data may not be correct")
            return False,[]
        (payments_calculated,purchases_calculated) = self.get_total_credits_debits()

        '''
        Suppose we take an EMI in HSBC it would comes like that. Say EMI is X and Interest is Y and Terms in T
        DESCRIPTION X Rs -> Debit transaction
        Description X CR -> Credit transaction
        Description nth/nnd/nst OF  T installments (X + Y)/T

        Summary
        Purchase&Other Charges -> Total Purchases (excluding any transaction related to X Rs) + X + Y
        '''
        loans = self.restructure_loans(loan_line_item_descriptions)
        loan_amount_with_interest = sum(map(lambda x:loans[x]["principal_and_interest"],loans))

        if abs(payments_calculated) != abs(payments_from_statement_summary):
            print("Calculated values and Value from Statement summary do not match for payemnts.Not proceeding")
            return False,[] 
        if abs(purchases_calculated) != abs(purchases_from_statement_summary):
            #Verify the EMI part
            if (abs(purchases_from_statement_summary) - purchases_calculated - loan_amount_with_interest) < \
                HSBCCCStatementProcessor.HDFC_PURCHASE_ERROR_THRESHOLD_WITH_LOANS:
                print("Loan Amounts were detected. Restructuring the transaction structures")
                transactions = self.create_transaction_table()
                for loan in loans:
                    transactions.append( \
                        TransactionCollectionModel() \
                            .src(self.accountInfo.GetaccountNumber()) \
                            .dest("EXTERNAL") \
                            .desc("%s - INTEREST"%loan) \
                            .amount(loans[loan]["interest"]) \
                            .txnType(TransactionType.DEBIT) \
                            .date(self.dateLineProcessor.GetValues()[-1].Getvalue().Getdate()) \
                            .txnId("%s%d"%(self.fileInfo.GetfileKey(),-1)))
                return True,transactions

            else: 
                print("Calculated values and Value from Statement summary do not match for purchases.Not proceeding")
                return False,[] 


        return True,self.create_transaction_table()