
'''Process the description value from statement lines'''
from typing import List, Optional
from statement_file_processor.processors.statement_processors.line_processors.regex_line_processor\
      import RegexLineProcessor
from statement_file_processor.data_types.description_value import DescriptionValue


class DescriptionLineProcessor(RegexLineProcessor):
    '''Process the description value from statement lines'''

    def __init__(self):
        RegexLineProcessor.__init__(self, "description")
        # TODO: Change the +/- [Space] Integer check to no match regex
        self.set_fetch_value_from_line_function(self.process_description)

    def process_description(self, line: Optional[str]) -> Optional[DescriptionValue]:
        '''Extracting the description value from the line'''
        # Putting a small restriction on linelength
        if line is not None and len(line) > 2:
            # Ignoring any integer descriptions
            try:
                if int(line.replace(' ', '')):
                    return None
            except ValueError:
                return DescriptionValue().description(line)
        return None

    def get_regex_line_no_match(self) -> List[str]:
        return [
            # Avoid the amounts being caputred accidentaly
            "^(\\d,)?(\\d\\d?,)?(\\d?\\d?\\d).\\d\\d$", 
            # Dates
            "^(\\d{2})/(\\d{2})/(\\d{4})$",
            # Dates
            "^(\\d{2})/(\\d{2})/(\\d{4}) (\\d{2}):(\\d{2}):(\\d{2})$",
            # Amounts or percentages eg: - 123, -34, 56% ..etc
            "^-?\\s*\\d+\\%?$",
            # To avoid series of perentages eg: 4% 5%, 67% 6% 7%..etc
            "^((\\d\\d?%)[ ]*)*$",
            "^\\d+][.]\\d{2}",
            # Remvoving amount representations eg:12.29 1,23.68 ..etc
            "^([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9] \\w{2}?$",
            # Remvoing invoice number description which is getting captured
            "^Invoice No: \\d+$",
            # Remving SIL number description
            "^CIN No. ([A-Z0-9])+$"
        ]
    
    def get_regex_line_match(self) -> List[str]:
        return [
            ""
        ]