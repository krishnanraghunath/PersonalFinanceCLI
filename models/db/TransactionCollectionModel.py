from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.transactions.DateValue import DateValue
from PersonalFinanceCLI.models.db.Enums import TransactionType

class TransactionCollectionModel(BaseDBModel):
    CollectionName = "transactions"
    def __init__(self,no_transforms=False):
        self.transforms = {
            "txnType" : lambda x:x._name_,
            "amount" : lambda x: float(x),
            "credit" : lambda x: float(x),
            "debit" : lambda x: float(x),
        }
        self.fields = [
            "txnId",
            "src",
            "dest",
            "desc",
            "amount",
            "date",
            "txnType", #Should be an enum in TransactionType
            #Following fields are only for printing.
            "credit", 
            "debit",
        ]
        self.hashfields = [
            #We are using following to identify a uniq transaction
            "src",
            "txnId",
            "txnType",
            "amount",
            "date"
        ]
        self.printtable = {
            "txnId" : "Transaction ID",
            "src" : "Source Account",
            "dest": "Destination Account",
            "desc":"Description",
            "amount":"Amount",
            "date":"Date",
            "credit": "Credit Amount" ,
            "debit": "Debit Amount" ,
        }
        self.printfunc = {
            "desc" : lambda x:x[:100],
            "date" : lambda x:DateValue.DateToString(x)
        }
        super().__init__(no_transforms)
    
    def refreshCreditsDebits(self):
        if self.GettxnType() == TransactionType.CREDIT.name:
            self.credit(self.Getamount())
        if self.GettxnType() == TransactionType.DEBIT.name:
            self.debit(self.Getamount())
    
    def refreshAmountTransactionType(self):
        self.amount(0).txnType(TransactionType.DEBIT)
        amount = self.Getcredit() - self.Getdebit()
        self.amount(abs(amount))
        if amount < 0:
            self.txnType(TransactionType.DEBIT)
        else:
            self.txnType(TransactionType.CREDIT)
        self.credit(None).debit(None)
        return self
    
    def sanitiseTransactionID(self):
        try:
            txnId = int(self.GettxnId())
            if txnId == 0:
                txnId = int(self.Getamount())
            self.txnId(str(txnId))
            return self
        except:
            pass
        return self



    def setAlignment(self,table):
        table.align["Description"] = 'l'
    
    def GetActualAmount(self):
        amountPrefix = '-'
        if self.GettxnType() == TransactionType.CREDIT:
            amountPrefix = "+"
        return amountPrefix+str(self.Getamount())