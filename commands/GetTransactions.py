from PersonalFinanceCLI.models.arguments.GetTransactionsArgument import GetTransactionsArgument
from PersonalFinanceCLI.commands.BaseCommand import BaseCommand
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.db.TagRuleModel import TagRuleModel
from PersonalFinanceCLI.models.db.TagCollectionModel import TagCollectionModel
from PersonalFinanceCLI.models.db.TotalCashFlow import TotalCashFlow
from PersonalFinanceCLI.db.TransactionCollectionClient import TransactionCollectionClient

class GetTransactions(BaseCommand):
    def __init__(self,cmdLineArgs):
        self.arguments = GetTransactionsArgument()
        self.transactionClient = TransactionCollectionClient()
        super().__init__(self.arguments,cmdLineArgs)
        self.arguments.validate()
        self.fromDate = 0
        self.toDate = 10000000000000
        self.minAmount = 0
        self.maxAmount = 100000000000
        self.regexDesc = None
        self.accounts = None 

    def _run(self):
        accountNumbers = self.arguments.GetaccountNumber()
        tagCollectionQuery = TagCollectionModel().accountNumbers(accountNumbers).rules(
            TagRuleModel().amountMin(self.arguments.Getamountgt()).amountMax(self.arguments.Getamountlt()) \
            .dateFrom(self.arguments.Getfrom()).dateTo(self.arguments.Getto())
            .descriptionRegex(self.arguments.Getrdesc())
        )
        self.tableSet(TransactionCollectionModel,title = "Transactions")
        projected_items = TransactionCollectionModel(1).src(1).desc(1).amount(1).txnType(1).date(1)

        cashFlows = {}
        totalCashflow = TotalCashFlow.DefaultTotalCashFlow("All Transactions")
        for transaction in self.transactionClient.get_transactions(tagCollectionQuery.GetMongoDBQueryForTransaction()
                                                                    ,projected_items):
            accountNumber = transaction.Getsrc()
            if accountNumber not in cashFlows:
                cashFlows[accountNumber] = TotalCashFlow.DefaultTotalCashFlow(accountNumber)
            cashFlows[accountNumber].mergeTransaction(transaction)
            totalCashflow.mergeTransaction(transaction)
            transaction.refreshCreditsDebits()
            self.tablePut(transaction)
        self.tablePrint(TransactionCollectionModel(1).src(1).desc(1).credit(1).date(1).debit(1))

        self.tableReset()
        self.tableSet(TotalCashFlow,title = "AccountWise Summary")
        [self.tablePut(cashFlows[x]) for x in cashFlows]
        if len(cashFlows) != 1:
            self.tablePut(totalCashflow)

        self.tablePrint(TotalCashFlow(1).identifier(1).credittxns(1).debittxns(1).txns(1)\
                                            .ldate(1).rdate(1).credit(1).debit(1).days(1).net(1))
        # return 
        self.tableReset()
        summaryCashflows = []
        [summaryCashflows.extend(cashFlows[x].getPeriodSummary()) for x in cashFlows]
        self.tableSet(TotalCashFlow,"Account Summary on Days/Months/Years",summaryCashflows[0])
        [self.tablePut(x) for x in summaryCashflows]
        self.tablePrint(TotalCashFlow(1).identifier(1).credittxns(1).debittxns(1).txns(1)\
                                           .credit(1).debit(1).net(1).day(1).month(1).year(1))


            

      