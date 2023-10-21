'''Collection datatype model for AccountCollection'''
from typing import Any, Dict, Callable, List
from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from PersonalFinanceCLI.models.db.Enums import AccountType, Banks, EnumUtil


class AccountCollectionModel(BaseDBModel):
    '''Collection datatype model for AccountCollection'''
    CollectionName = "accounts"

    def get_fields(self) -> List[str]:
        return [
            "account_number",
            "account_name",
            "account_bank",
            "account_type",
        ]

    def get_hash_fields(self) -> List[str]:
        return [
            "account_number"
        ]

    def get_data_transform_map(self) -> Dict[str, Callable[[str], Any]]:
        return {
            "account_bank": lambda x: EnumUtil.convert_enum_value_to_text(x, Banks),
            "account_type": lambda x: EnumUtil.convert_enum_value_to_text(x, AccountType)
        }
