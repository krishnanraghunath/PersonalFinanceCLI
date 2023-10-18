from PersonalFinanceCLI.processors.statement_processors.line_processors.regex_line_processor import RegexLineProcessor
from PersonalFinanceCLI.models.transactions.DescriptionValue import DescriptionValue 
class DescriptionLineProcessor(RegexLineProcessor):
    def __init__(self):
        RegexLineProcessor.__init__(self)
        self.set_match_regexes([''])
        self.set_no_match_regexes([
             "^\d+.\d{2}", #Avoid the amounts being caputred accidentaly
            "^(\d{2})/(\d{2})/(\d{4})$", # Dates
            "^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2})$", #Dates
            "^-?\s*\d+\%?$", # Amounts or percentages eg: - 123, -34, 56% ..etc
            "^((\d\d?%)[ ]*)*$",# To avoid series of perentages eg: 4% 5%, 67% 6% 7%..etc
            "^\d+][.]\d{2}",
            "^([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9] \w{2}?$",#Remvoving amount representations eg:12.29 1,23.68 ..etc
            ]
            )
        #TODO: Change the +/- [Space] Integer check to no match regex
        self.SetFetchFunction(self.process_description)
        pass

    def process_description(self,line):
        try:
            if line != None and len(line) > 2: #Putting a small restriction on linep
                try:
                    intVal = int(line.replace(' ',''))
                    return None
                except:
                    return DescriptionValue().description(line)
        except:
            return None

