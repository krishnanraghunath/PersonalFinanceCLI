from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.db.TagRuleModel import TagRuleModel
from PersonalFinanceCLI.models.db.Enums import TransactionType
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.MongoDBQueryModel import MongoDBQueryModel

class TagCollectionModel(BaseDBModel):

    CollectionName = "tags"
    def __init__(self):
        self.fields = [
            "tagName",
            "accountNumbers",
            "rules"
        ]

        self.hashfields = [
            "tagName"
        ]
        self.printtable = {
            "tagName" : "Tag Name",
            "accountNumbers" : "Account Numbers",
            "rules": "Tag Rules"
        }
        # self.printfunc = {
        #     "rules" : lambda x:x.PrettyString
        # }
        super().__init__()
    
    def GetMongoDBQueryForTransaction(self):
        if not isinstance(self.Getrules(),TagRuleModel):
            return None
        #This would make sure values are correct transformed and unwanted are discarded
        rules = TagRuleModel().ingest(~self.Getrules())
        minAmount = rules.GetamountMin()  if rules.GetamountMin() else 0
        maxAmount = rules.GetamountMax()  if rules.GetamountMax() else 10000000000000
        fromDate = rules.GetdateFrom()  if rules.GetdateFrom() else 0
        toDate = rules.GetdateTo()  if rules.GetdateTo() else 10000000000000
        return TransactionCollectionModel(1) \
                    .src(MongoDBQueryModel().In(self.GetaccountNumbers())) \
                    .amount(MongoDBQueryModel().gt(minAmount-1).lt(maxAmount+1))\
                    .date(MongoDBQueryModel().gt(fromDate-1).lt(toDate+1)) \
                    .desc(MongoDBQueryModel().regex(rules.GetdescriptionRegex()))
        #Check for the rules


