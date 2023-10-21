'''Tag Collection Model'''
from __future__ import annotations
from typing import Dict, List, Callable
from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.db.TagRuleModel import TagRuleModel
from PersonalFinanceCLI.models.db.Enums import TransactionType
from PersonalFinanceCLI.models.db.TransactionCollectionModel import TransactionCollectionModel
from PersonalFinanceCLI.models.MongoDBQueryModel import MongoDBQueryModel

class TagCollectionModel(BaseDBModel):
    '''Tag Collection Model'''
    CollectionName = "tags"
    def __init__(self) -> None:
        super().__init__()
        self.get_rules: Callable[[], TagRuleModel]
        self.rules: Callable[[TagRuleModel], TagCollectionModel]
        self.get_account_numbers: Callable[[], List[int]]
    
    def get_mongo_db_query_for_transaction(self) -> TransactionCollectionModel:
        #This would make sure values are correct transformed and unwanted are discarded
        rules: TagRuleModel = TagRuleModel().ingest(~self.get_rules()) # type: ignore
        minimum_amount = rules.get_amount_min()  if rules.get_amount_min() else 0
        maximum_amount = rules.get_amount_max()  if rules.get_amount_max() else 10000000000000
        from_date = rules.get_date_from()  if rules.get_date_from() else 0
        to_date = rules.get_date_to()  if rules.get_date_to() else 10000000000000
        return TransactionCollectionModel(1) \
                    .src(MongoDBQueryModel().In(self.get_account_numbers())) \
                    .amount(MongoDBQueryModel().gt(minimum_amount-1).lt(maximum_amount+1))\
                    .date(MongoDBQueryModel().gt(from_date-1).lt(to_date+1)) \
                    .desc(MongoDBQueryModel().regex(rules.get_description_regex()))
        #Check for the rules

    def get_hash_fields(self) -> List[str]:
        return [
            "tag_name"
        ]

    def get_fields(self) -> List[str]:
        return [
            "tag_name",
            "account_numbers",
            "rules"
        ]
    
    def get_field_to_column_names(self) -> Dict[str, str]:
        return {
            "tagName" : "Tag Name",
            "accountNumbers" : "Account Numbers",
            "rules": "Tag Rules"
        }