from PersonalFinanceCLI.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
from PersonalFinanceCLI.models.transactions.DateValue import DateValue
import datetime
from re import compile
class DateLineProcessor(RegexLineProcessor):
    def __init__(self):
        RegexLineProcessor.__init__(self)
        self.set_match_regexes(["^(\d{2})/(\d{2})/(\d{4})$",
        "^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2})$"])
        self.SetFetchFunction(self.process_date)
        pass

    def process_date(self,line):
        try:
            (day,month,year) = compile("(\d{2})/(\d\d?)/(\d{4})").search(line).groups()
            dt = datetime.datetime(year=int(year), month=int(month), day=int(day))
            # Also checking it if is a later date than say 01/01/2015 and less than a near future date
            # (it should be tomorrow ideally) --> TODO: Make sensible comparison
            # (some valid close enough date and  which will be alwasy in past in terms of statements)
            #100 YEARS OF ME!!
            if datetime.datetime(year=1990, month=4, day=20) < dt < datetime.datetime(year=2090, month=4, day=20):
                return DateValue().date(int(dt.timestamp()*1000))
        except Exception as e:
            print(e)
            pass
        return None

