''' This would act as a common class which can be used to any object which would 
represent a json object or a data type. It would self generate the get and set functions as well'''
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Callable, Any, Type
from json import loads
from json.decoder import JSONDecodeError


class BaseModel(ABC):
    '''For each field 2 functions will be created
     fn:<fieldName> () --> Set Value
    fn: Get<fieldName > () --> Get Value
    '''

    def __init__(self, json_object: Optional[Dict[str, Any]] = None) -> None:
        for field in self.get_fields():
            setattr(self, field, self._function_set('_' + field))
            setattr(self, 'get_'+field, self._function_get('_' + field))
        if json_object is not None:
            self.ingest(json_object)

    def ingest(self, json_object: Optional[Dict[str, Any]]) -> Type[BaseModel]:
        '''
        For eg:
        Class Defenition
        -> Account => 13,TransactionID =>345 
        Input Dict/Json
        -> Account =>13, transaction_id => 345
        => So field map would be => {"TransactionID" : "transaction_id"}
        '''
        if json_object is None:
            return self
        try:
            _json_object = json_object
            if isinstance(json_object, str):
                _json_object = loads(json_object)
            # Copy the fields to class based on field -> json Field map'''
            _f1 = [self._set_value('_'+x, _json_object[self.get_key_to_field_map()[x]]) for x in
                   filter(lambda y:self.get_key_to_field_map()[y] in _json_object,
                          filter(lambda z:z in self.get_key_to_field_map(), self.get_fields()))]
            # Copy the all the deined fields (assuming field == jsonField name for all fields)'''
            _f2 = [self._set_value('_' + x, _json_object[x]) for x in
                   filter(lambda y: y in _json_object, self.get_fields())]
        except JSONDecodeError:
            pass
        except TypeError:
            pass
        return self

    def __invert__(self) -> Dict[str, Any]:
        '''Return a dict of field -> value'''
        kwargs: Dict[str, Any] = {}
        for field in self.get_fields():
            attribute_value = getattr(self, '_'+field)
            if attribute_value is not None:
                _transform_map = self.get_data_transform_map()
                if field in _transform_map:
                    attribute_value = _transform_map[field](
                        attribute_value)
                if isinstance(attribute_value, BaseModel):
                    attribute_value = ~attribute_value
                if attribute_value is not None:
                    kwargs[self.get_key_appender()+field] = attribute_value
        return kwargs

    def _function_set(self, field: str) -> Callable[[str], BaseModel]:
        return lambda x: self._set_value(field, x)

    def _function_get(self, field: str) -> Callable[[], Any]:
        return lambda: self._get_value(field)

    def _set_value(self, field: str, value: Any):
        setattr(self, field, value)
        return self

    def _get_value(self, field: str) -> Any:
        try:
            return getattr(self, field)
        except AttributeError:
            return None

    @abstractmethod
    def get_fields(self) -> List[str]:
        '''Should be overriden in the base class to give the field names of the function'''
        return []
    
    def get_key_appender(self) -> str:
        '''Get the key to be appended for the key:value'''
        return ','
    
    def get_key_to_field_map(self) -> Dict[str, str]:
        '''Get key in inbound json object => field in the json object map'''
        return {}

    def get_data_transform_map(self) -> Dict[str, Callable[[str], Any]]:
        '''Gee the field => transform(value of field) map'''
        return {}