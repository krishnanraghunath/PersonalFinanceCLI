from PersonalFinanceCLI.processors.statement_processors.csv_statement_processor import CSVStatementProcessor
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.db.Enums import TransactionType
from PersonalFinanceCLI.models.transactions.DateValue import DateValue

from decimal import Decimal
from functools import reduce



class HDFCBankAccountStatementProcessor(CSVStatementProcessor):
    THRESHOLD = 1
    JSON_FIELD_MAP =  {
        "date" :"Date",
        "desc" : "Narration" ,
        "debit" : "Debit Amount",
        "credit" :"Credit Amount" ,
        "txnId" : "Chq/Ref Number" ,
        "amount": "Closing Balance" ,
    }

    def __init__(self,fileInfo,accountInfo):
        CSVStatementProcessor.__init__(self,fileInfo,accountInfo,HDFCBankAccountStatementProcessor.JSON_FIELD_MAP)
   


    def process(self):
        transactions = []
        '''Find all the transactions'''
        for line in self.lines:
            transaction = TransactionCollectionModel().ingest(line,HDFCBankAccountStatementProcessor.JSON_FIELD_MAP)
            transaction.date(DateValue.ddmmyy_to_timestamp(transaction.Getdate()))
            transaction.src(self.accountInfo.GetaccountNumber())
            transaction.dest("EXTERNAL")
            transaction = TransactionCollectionModel().ingest(~transaction)
            if transaction.Getdebit() == None:
                        transaction.debit(0)
            if transaction.Getcredit() == None:
                transaction.credit(0)
            transactions.append(transaction)
     
        #Verify if the file name of the uploaded object starts with the account number itself.(Downloaded statement
        #  files will start with account number for HDFC)
        print("Verifying Account Information")
        if not self.fileInfo.GetfileLoc().split('/')[-1].startswith(self.accountInfo.GetaccountNumber()):
            print("Account number do not match with the given file. (File name would usually starts with the acount number for the account")
            return False,[]


        #Verify if we have missed any transactions. if we have missed the transactions will not tally
        print("Information Integrity check")
        openinging_balance = transactions[0].Getamount()
        closing_balance = transactions[-1].Getamount()
        total_transactions = reduce(lambda x,y:x + y,map(lambda z:z.Getcredit()-z.Getdebit(),transactions[1:]))
        if abs(openinging_balance + total_transactions - closing_balance) > HDFCBankAccountStatementProcessor.THRESHOLD:
            return False,[]

        #.sanitiseTransactionID() getting called becaus amount would be closing balance. So distinct transacctions with similar features like
        # amount, txn Type, desc..etc will have different txnIds based on amount (closing balance at the moment as per design)
        return True,[t.sanitiseTransactionID().refreshAmountTransactionType()for t in transactions]