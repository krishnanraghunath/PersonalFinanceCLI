# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.pdfpage import PDFPage
# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
import io
# from functools import reduce

# from PersonalFinanceCLI.processors.statement_processors.line_processors.amount_line_processor import AmountLineProcessor
# from PersonalFinanceCLI.processors.statement_processors.line_processors.date_line_processor import DateLineProcessor
# from PersonalFinanceCLI.processors.statement_processors.line_processors.description_line_processor import DescriptionLineProcessor
# from PersonalFinanceCLI.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
# from PersonalFinanceCLI.processors.statement_processors.common  import PDF_STATEMENT_PROCESSOR
# from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
# from PersonalFinanceCLI.models.db.Enums import TransactionType
import csv

class CSVStatementProcessor:

    def __init__(self,fileInfo,accountInfo,fieldMap = {}):
        self.fileInfo = fileInfo
        self.accountInfo = accountInfo
        self.fieldMap = fieldMap
        

    def initialise(self,seperator=","):
        response,lines = self._fetch_data()
        '''
        Need to take care of descriptions having seperators in them
        For that if we asssume first line split happens without any issues,we can 
        findout the description by making sure total length of array is equal to total length of
        values and knowing from which index the description starts
        '''

        descriptionField = 'desc'
        if descriptionField in self.fieldMap:
            descriptionField = self.fieldMap[descriptionField]
        if response:
            lines = [[y.strip() for y in x.split(seperator)] for x in lines]
            self.headers = {x:lines[0].index(x) for x in lines[0]}
            descriptionIndex = self.headers[descriptionField]
            headerLength = len(self.headers)
            self.lines = []
            for line in lines[1:]:
                new_line = line[:descriptionIndex]
                new_line.extend(line[-(headerLength-descriptionIndex-1):])
                new_line.insert(descriptionIndex,' '.join(line[descriptionIndex:-(headerLength-descriptionIndex-1)]))
                self.lines.append({x:new_line[self.headers[x]] for x in self.headers})
        return response

    def process(self):
        print("Process method not overridden.")
        return False,None

    def _fetch_data(self):
        try:
            return True,list(filter(lambda x:len(x) > 0,self.fileInfo.GetfileObject().decode().splitlines()))
        except:
            import traceback
            traceback.print_exc()
            return False,None   
            
    # def create_transaction_table(self):
    #     transactions = []
    #     accountNumber = self.accountInfo.GetaccountNumber()
    #     fileKey = self.fileInfo.GetfileKey()
    #     dates = self.dateLineProcessor.GetValues()
    #     amounts = self.amountLineProcessor.GetValues()
    #     descriptions = self.descriptionLineProcessor.GetValues()
    #     totalCount =  self.descriptionLineProcessor.GetTotalValues()
    #     transactions = [ TransactionCollectionModel()
    #                         .src(accountNumber)
    #                         .dest("EXTERNAL")
    #                         .desc(descriptions[x].Getvalue().Getdescription())
    #                         .amount(amounts[x].Getvalue().Getamount())
    #                         .txnType(amounts[x].Getvalue().GettxnType())
    #                         .date(dates[x].Getvalue().Getdate())
    #                         #Uniquley identify the transaction based on statement file and line number
    #                         #Since it wont be changes regardless of re-uploading
    #                         .txnId("%s%d"%(fileKey,amounts[x].Getline()))
    #                     for x in range(0,totalCount)]
    #     return transactions
    
    # def verify_account_details(self):
    #     if self.accountDetailsProcessor.GetTotalValues == 0:
    #         print("Unable to capture any card number related details")
    #         return False
    #     cardDetails = self.accountDetailsProcessor.GetValues()
    #     accountNumber = cardDetails[-1].Getvalue().GetcardNumber()
    #     accountNumberProvided = self.accountInfo.GetaccountNumber()
    #     if accountNumber[:2] + accountNumber[-4:] != accountNumberProvided[:2] + accountNumberProvided[-4:]:
    #         print("Mismatch in Account Number Provided %s and Account Number %s" \
    #                                         %(accountNumberProvided,accountNumber))
    #         return False 
    #     return True
    
    # def get_total_credits_debits(self):
    #     return self.get_total_credits_debits_for_values(self.amountLineProcessor.GetValues())
      
    # def get_total_credits_debits_for_values(self,values):
    #     get_amount_based_on_txnType = lambda x,y: \
    #                     x.Getvalue().Getamount() \
    #                     if x.Getvalue().GettxnType() == y \
    #                     else 0
    #     return (
    #             reduce(lambda x,y:x+y,
    #                         map(lambda z: get_amount_based_on_txnType(z,TransactionType.CREDIT),
    #                                      values)),
    #             reduce(lambda x,y:x+y,
    #                         map(lambda z: get_amount_based_on_txnType(z,TransactionType.DEBIT),
    #                                       values)),
    #             )

