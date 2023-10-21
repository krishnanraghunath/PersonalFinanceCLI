'''Base DB Model which will would be extended for each DB collection data type'''
from __future__ import annotations
from typing import Callable, Dict, Union, List, Any
from abc import abstractmethod
from hashlib import md5
from PersonalFinanceCLI.models.BaseModel import BaseModel


class BaseDBModel(BaseModel):
    '''Base DB Model which will would be extended for each DB collection data type'''

    @staticmethod
    def md5_hash(hash_func: Callable[[BaseDBModel], str]) -> Callable[[BaseDBModel], str]:
        '''Return a function which would be returing the hexdigest of the given string'''
        def md5_hash(obj: BaseDBModel) -> str:
            return md5(hash_func(obj).encode("utf-8")).hexdigest()
        return md5_hash

    def __init__(self) -> None:
        super().__init__()

    @md5_hash
    def hash(self) -> str:
        '''Just returing the hash using primary keys'''
        hash_value = ''
        object_json_repr = ~self
        for _hash_field in self.get_hash_fields():
            hash_value = hash_value + str(object_json_repr[_hash_field])
        return hash_value

    @abstractmethod
    def get_hash_fields(self) -> List[str]:
        '''Get the hash fields to create the key for the db object'''
        return []

    def get_column_names(self, include_all: bool = True) -> List[str]:
        '''Get the column names to be printed when displaying the data
            through console/command line'''
        columns: List[str] = []
        _field_to_column_name_map = self.get_field_to_column_names()
        for _field_name in self.__get_fields():
            if include_all and _field_name in _field_to_column_name_map:
                columns.append(_field_to_column_name_map[_field_name])
            if not include_all and _field_name in _field_to_column_name_map and\
                    self._function_get('_' + _field_name)() is not None:
                columns.append(_field_to_column_name_map[_field_name])
        return columns

    def get_as_row(self) -> List[str]:
        '''Get the value of the object as a row which can be printed'''
        row_values: List[str] = []
        _field_to_column_name = self.get_field_to_column_names()
        _field_value_to_row_value_funcs = \
            self.get_field_value_to_row_value_map_functions()
        for _field_name in self.__get_fields():
            if _field_name not in _field_to_column_name:
                continue
            try:
                if getattr(self, '_'+_field_name) is not None:
                    if _field_name in _field_value_to_row_value_funcs:
                        row_values.append(
                            _field_value_to_row_value_funcs[_field_name](
                                getattr(self, '_'+_field_name)))
                    elif isinstance(getattr(self, '_'+_field_name), BaseDBModel):
                        row_values.append(str(
                            getattr(self, '_'+_field_name).pretty_string()))
                    else:
                        row_values.append(str(getattr(self, '_'+_field_name)))
                else:
                    row_values.append('')
            except ValueError:
                row_values.append('')
        return row_values

    # def set_alignment(self, table):
     #   pass

    def pretty_string(self) -> Union[Dict[str, Any], str]:
        '''Return a printable represetation of the object'''
        return ~self

    @abstractmethod
    def get_field_to_column_names(self) -> Dict[str, str]:
        '''Get a mapping of local field names to the Table 
            column name'''
        return {}

    @abstractmethod
    def get_field_value_to_row_value_map_functions(self)\
            -> Dict[str, Callable[[Any], str]]:
        '''Get a mapping of local field names to the Table 
            column name'''
        return {}

    def __get_fields(self) -> List[str]:
        '''Return the fields + adding required fields'''
        __fields = self.get_fields()
        __fields.append('_id')
        __fields.append('_error_code')
        return __fields
