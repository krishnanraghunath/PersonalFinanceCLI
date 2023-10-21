from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.transactions.DateValue import DateValue
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.db.Enums import TransactionType
from re import compile 


class TotalCashFlow(BaseDBModel):
    '''
    There are no DBs/Collection Associated with this one. As of now we are just using it for
    displaying the aggragated cashflow for instruments using this one
    '''
    @staticmethod
    def DefaultTotalCashFlow(identifier = None):
        return TotalCashFlow().identifier(identifier).credittxns(0).debittxns(0).txns(0)\
            .ldate(100000000000000000).rdate(0).credit(0).debit(0).days(0).net(0).day({}).month({}).year({})

    CollectionName = "transactions"
    def __init__(self,no_transforms=False):
        self.transforms = {
            "txnType" : lambda x:x._name_,
            "amount" : lambda x: float(x)
        }
        self.fields = [
            "identifier",
            #For displaying aggragate on days/months/year
            "day",
            "month",
            "year",
            ###
            "ldate",
            "rdate",
            "days", 
            "credittxns",
            "debittxns",
            "txns",
            "credit",
            "debit",
            "net",  
        ]
        self.hashfields = []

        self.printtable = {
            "identifier" : "Summary Name",
            "day" : "Day",
            "month" : "Month",
            "year" : "Year",
            "ldate" : "Start Date",
            "rdate" : "End Date",
            "credit" : "Credit Amounts",
            "debit" : "Debit Amounts",
            "days" : "Total Days",
            "net": "Net Amount",
            "credittxns" : "Credits",
            "debittxns" : "Debits",
            "txns" : "Count"
        }
        self.print_function = {
            "ldate" : DateValue.date_to_string,
            "rdate" : DateValue.date_to_string,
            "debit" : lambda x: "%.2f"%x,
            "credit" : lambda x: "%.2f"%x,
            "net": lambda x: "%.2f"%x
        }
        super().__init__(no_transforms)
    
    def set_alignment(self,table):
        table.align["Summary Name"] = 'l'
     

    def getPeriodSummary(self):
        summary = []
        days = list(self.Getday().values())
        months = list(self.Getmonth().values())
        years = list(self.Getyear().values())

        if len(months) == 1: summary.extend(days)
        if len(months) < 3 and len(days)< 10: summary.extend(months)
        if len(years) == 1 and len(days) < 10: summary.extend(years)
        if len(years) > 1 and len(days) > 10:
            summary = months
            summary.extend(years)
        return summary
        

    def mergeTransaction(self,transaction,aggregate = True):
        if not isinstance(transaction,TransactionCollectionModel):
            return 
        if transaction.GettxnType() == TransactionType.CREDIT.name:
            self.credit(self.Getcredit()+transaction.Getamount())
            self.credittxns(self.Getcredittxns() + 1)
        if transaction.GettxnType() == TransactionType.DEBIT.name:
            self.debit(self.Getdebit()+transaction.Getamount())
            self.debittxns(self.Getdebittxns() + 1)
        if self.Getrdate() < transaction.Getdate():
            self.rdate(transaction.Getdate())
        if self.Getldate() > transaction.Getdate():
            self.ldate(transaction.Getdate())
        self.net(self.Getcredit() - self.Getdebit())
        self.days(int((self.Getrdate() - self.Getldate())/(86400*1000)))
        self.txns(self.Getcredittxns() + self.Getdebittxns())

        if not aggregate:
            return 
        
        (dayK,day,monthK,month,yearK,year) = compile("^((\d\d?)-((\d\d?)-((\d{4}))))$").search( DateValue.date_to_string(transaction.Getdate())).groups()

        totalCashFlow = lambda x,y,z: TotalCashFlow.DefaultTotalCashFlow().day(z).month(y).year(x)
        identifer = self.Getidentifier()
        if yearK not in self.Getyear():
            self.Getyear()[yearK] =totalCashFlow(year,None,None).identifier("%10s (Yearly)  %s"%(year,identifer))
        if  monthK not in self.Getmonth():
            self.Getmonth()[monthK] = totalCashFlow(year,month,None).identifier("%5s/%s (Monthly) %s"%(month,year,identifer))
        if  dayK not in self.Getday():
            self.Getday()[dayK] = totalCashFlow(year,month,day).identifier("%s/%s/%s (Daily)   %s"%(month,day,year,identifer))
        self.Getyear()[yearK].mergeTransaction(transaction,False)
        self.Getmonth()[monthK].mergeTransaction(transaction,False)
        self.Getday()[dayK].mergeTransaction(transaction,False)

        