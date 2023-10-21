'''Date Value model'''
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from re import compile as compile_regex
from PersonalFinanceCLI.models.BaseModel import BaseModel


class DateValue(BaseModel):
    '''Date Value model'''

    def __init__(self):

        self.fields = [
            "date"
        ]
        super().__init__()

    @staticmethod
    def date_to_string(date: int) -> str:
        '''Convert given date in ms to a string in dd-mm-yy format'''
        return datetime.fromtimestamp(date/1000).strftime('%d-%m-%Y')

    @staticmethod
    def ddmmyy_to_timestamp(date: str) -> Optional[int]:
        '''Return a timestamp from a given date string in dd/mm/yy
          format or an int timestamp'''
        date_regex = compile_regex('''^(\\d\\d?)/(\\d\\d?)/(\\d{2})$''')
        try:
            # 100 years of me!!
            # Try if a timestamp is already passed
            if int(date) > 640580700000 and int(date) < 3796340700000:
                return int(date)
        except ValueError:
            pass
        try:
            dd, mm, yy = date_regex.findall(date)[0]
            return int(datetime(year=int(yy)+2000, month=int(mm), day=int(dd)).timestamp()*1000)
        except IndexError:
            pass
        except ValueError:
            pass
        return None

    def get_data_transform_map(self) -> Dict[str, Callable[[Any], Any]]:
        return {
            "date": DateValue.date_to_string
        }

    def get_fields(self) -> List[str]:
        return [
            "date"
        ]
