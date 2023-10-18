from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io
from functools import reduce

from PersonalFinanceCLI.processors.statement_processors.line_processors.amount_line_processor import AmountLineProcessor
from PersonalFinanceCLI.processors.statement_processors.line_processors.date_line_processor import DateLineProcessor
from PersonalFinanceCLI.processors.statement_processors.line_processors.description_line_processor import DescriptionLineProcessor
from PersonalFinanceCLI.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
from PersonalFinanceCLI.processors.statement_processors.common  import PDF_STATEMENT_PROCESSOR
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.db.Enums import TransactionType

class PDFStatementProcessor:

    def __init__(self,fileInfo,accountInfo):
        self.fileInfo = fileInfo
        self.accountInfo = accountInfo
        self.amountLineProcessor = AmountLineProcessor()
        self.descriptionLineProcessor = DescriptionLineProcessor()
        self.dateLineProcessor = DateLineProcessor()
        self.accountDetailsProcessor = RegexLineProcessor()
        #Few Generic initialisations
        self.amountLineProcessor.set_start_regexes(PDF_STATEMENT_PROCESSOR.AMOUNT_LINE_START_REGEX)
        self.dateLineProcessor.set_start_regexes(PDF_STATEMENT_PROCESSOR.DATE_LINE_START_REGEX)
        

    def initialise(self):
        self.amountLineProcessor.initialise()
        self.descriptionLineProcessor.initialise()
        self.dateLineProcessor.initialise()
        self.accountDetailsProcessor.initialise()
        response,self.lines = self._fetch_data()
        f = open("pdftext.txt","w")
        f.write(self.lines)
        f.close()
        return response

    def process(self):
        print("Process method not overridden.")
        return False,None

    def _fetch_data(self):
        with io.BytesIO() as fileObject:
            try:
                fileObject.write(self.fileInfo.GetfileObject())
                resMgr = PDFResourceManager()
                retData = io.StringIO()
                TxtConverter = TextConverter(resMgr, retData, laparams=LAParams())
                interpreter = PDFPageInterpreter(resMgr, TxtConverter)
                for page in PDFPage.get_pages(fileObject):
                    interpreter.process_page(page)
                return True,retData.getvalue()
            except:
                import traceback
                traceback.print_exc()
                return False,None   
               
    def create_transaction_table(self):
        transactions = []
        accountNumber = self.accountInfo.GetaccountNumber()
        fileKey = self.fileInfo.GetfileKey()
        dates = self.dateLineProcessor.GetValues()
        amounts = self.amountLineProcessor.GetValues()
        descriptions = self.descriptionLineProcessor.GetValues()
        totalCount =  self.descriptionLineProcessor.GetTotalValues()
        transactions = [ TransactionCollectionModel()
                            .src(accountNumber)
                            .dest("EXTERNAL")
                            .desc(descriptions[x].Getvalue().Getdescription())
                            .amount(amounts[x].Getvalue().Getamount())
                            .txnType(amounts[x].Getvalue().GettxnType())
                            .date(dates[x].Getvalue().Getdate())
                            #Uniquley identify the transaction based on statement file and line number
                            #Since it wont be changes regardless of re-uploading
                            .txnId("%s%d"%(fileKey,amounts[x].Getline()))
                        for x in range(0,totalCount)]
        return transactions
    
    def verify_account_details(self):
        if self.accountDetailsProcessor.GetTotalValues == 0:
            print("Unable to capture any card number related details")
            return False
        cardDetails = self.accountDetailsProcessor.GetValues()
        accountNumber = cardDetails[-1].Getvalue().GetcardNumber()
        accountNumberProvided = self.accountInfo.GetaccountNumber()
        if accountNumber[:2] + accountNumber[-4:] != accountNumberProvided[:2] + accountNumberProvided[-4:]:
            print("Mismatch in Account Number Provided %s and Account Number %s" \
                                            %(accountNumberProvided,accountNumber))
            return False 
        return True
    
    def get_total_credits_debits(self):
        return self.get_total_credits_debits_for_values(self.amountLineProcessor.GetValues())
      
    def get_total_credits_debits_for_values(self,values):
        get_amount_based_on_txnType = lambda x,y: \
                        x.Getvalue().Getamount() \
                        if x.Getvalue().GettxnType() == y \
                        else 0
        return (
                reduce(lambda x,y:x+y,
                            map(lambda z: get_amount_based_on_txnType(z,TransactionType.CREDIT),
                                         values)),
                reduce(lambda x,y:x+y,
                            map(lambda z: get_amount_based_on_txnType(z,TransactionType.DEBIT),
                                          values)),
                )

