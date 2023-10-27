'''Process the date lines from the statement'''
import datetime
import re
from typing import List, Optional
from statement_file_processor.processors.statement_processors.line_processors.regex_line_processor\
    import RegexLineProcessor
from statement_file_processor.data_types.date_value import DateValue


class DateLineProcessor(RegexLineProcessor):
    '''Process the date lines from the statement'''

    def __init__(self):
        RegexLineProcessor.__init__(self, "date")
        self.set_fetch_value_from_line_function(self.process_date)

    def process_date(self, line: str) -> Optional[DateValue]:
        '''Extract date value from a given line'''
        try:
            _match = re.compile("(\\d{2})/(\\d\\d?)/(\\d{4})").\
                search(line)
            if _match:
                (day, month, year) = _match.groups()
                _processed_datetime = datetime.datetime(
                    year=int(year), month=int(month), day=int(day))
                # Also checking it if is a later date than say 01/01/2015 and less than a near future date
                # (it should be tomorrow ideally) --> TODO: Make sensible comparison
                # (some valid close enough date and  which will be always in past in terms of statements)
                # 100 YEARS OF ME!!
                if datetime.datetime(year=1990, month=4, day=20) < _processed_datetime\
                        < datetime.datetime(year=2090, month=4, day=20):
                    return DateValue().date(int(_processed_datetime.timestamp()*1000))
        except AttributeError:
            pass
        except ValueError:
            pass
        return None

    def get_regex_line_match(self) -> List[str]:
        return [
            "^(\\d{2})/(\\d{2})/(\\d{4})$",
            "^(\\d{2})/(\\d{2})/(\\d{4}) (\\d{2}):(\\d{2}):(\\d{2})$"]
