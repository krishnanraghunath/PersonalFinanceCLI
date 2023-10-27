'''Regex Line Processor to proess a given lines based on regex rules'''
import re
from typing import Any, Callable, List, Optional
from statement_file_processor.data_types.description_value import DescriptionValue
from statement_file_processor.data_types.data_blurb import DataBlurb
from statement_file_processor.data_types.data_value import DataValue, DataValueType
from statement_file_processor.data_types.data_value_list import DataValues

# Line Processor based on Regex on only for following single purpose
# 1 -> For a series of inputs
# 2 -> Decide when processor should get activated based on start regexes
# 3 -> See if the values are according to the format if it is activated based on match regex
# 4 -> Decide when processor should get deactivated based on stop egex


class RegexLineProcessor():
    '''Regex Line Processor to proess a given lines based on regex rules'''

    def __init__(self,processor_name: str = 'regex'):
        '''Regex Line Processor to proess a given lines based on regex rules'''
        self._processing = False
        self._processing_start_regexes: List[re.Pattern[Any]] = []
        self._processing_stop_regexes: List[re.Pattern[Any]] = []
        self._processing_match_regexes: List[re.Pattern[Any]] = []
        self._processing_no_match_regexes: List[re.Pattern[Any]] = []
        self._fetch_value_function: Callable[[
            str], DataValueType] = lambda x: DescriptionValue().description(x)
        self._pre_process_line: Callable[[str], str] = lambda x: x
        self._line_counter: int = 0
        self._values = DataValues().values([]).count(0)
        self._processor_name = processor_name
        self._initialise()
    
    def get_processor_name(self) -> str:
        '''Return the processor name'''
        return self._processor_name

    def is_processing(self) -> bool:
        '''Return if it is currently processing or not'''
        return self._processing

    def turn_on_processing(self) -> None:
        '''Turn on the processing flag'''
        self._processing = True

    def turn_off_processing(self) -> None:
        '''Turn off the processing flag'''
        self._processing = False

    def inc_line_count(self) -> None:
        '''Increment the line counter'''
        self._line_counter = self._line_counter + 1

    def get_line_count(self) -> int:
        '''returns the current line count'''
        return self._line_counter

    def _initialise(self):
        '''All the regexes will be used with OR combination, i.e 
        if any of the regex in a list matches that would be fine'''
        self._processing_start_regexes = [re.compile(
            x) for x in self.get_regex_processing_start()]
        self._processing_stop_regexes = [re.compile(
            x) for x in self.get_regex_processing_stop()]
        self._processing_match_regexes = [
            re.compile(x) for x in self.get_regex_line_match()]
        self._processing_no_match_regexes = [
            re.compile(x) for x in self.get_regex_line_no_match()]

    def process(self, line: str) -> bool:
        '''Process a given line'''
        self.inc_line_count()
        # Strip the line of extra spaces
        line = line.strip()
        # First verify if the line matches with that of processing stop regex
        if self._is_any_regex_match(line, self._get_regex_processing_stop()):
            self.turn_off_processing()
            return False
        if self.is_processing():
            # If the line matches with any rules with that of non matching pattern do not proceed
            if self._is_any_regex_match(line, self._get_regex_line_no_match()):
                return False
            # If the line matches with any rules with that of matching pattern proceed
            if self._is_any_regex_match(line, self._get_regex_line_match()):
                # Pre process the line (pre process could be overriden by child class)
                return self.add_line_data_to_values(line)
        # See if to turn on processing line processing
        # These lines will not be matched, only be used to turn on the flag
        if self._is_any_regex_match(line, self._get_regex_processing_start()):
            self.turn_on_processing()
        return False

    def get_total_lines_processed(self) -> int:
        '''To be deprecated'''
        return self._line_counter

    def get_total_data_values(self) -> int:
        '''Get the total number of collected data values'''
        return self._values.get_count()

    def set_fetch_value_from_line_function(self, function: Callable[[str], Any]) -> None:
        '''Set the function to fetch the value from given line'''
        self._fetch_value_function = function

    def set_pre_process_line_function(self, function: Callable[[str], str]):
        '''Set the preprocessing function'''
        self._pre_process_line = function

    def set_start_regexes(self, start_regex: Optional[List[str]] = None):
        '''Extend the Processing start regex'''
        if start_regex is not None:
            self._processing_start_regexes.extend(
                [re.compile(x) for x in start_regex])

    def set_stop_regexes(self, stop_regex: Optional[List[str]] = None):
        '''Extend the Processing stop regex'''
        if stop_regex is not None:
            self._processing_stop_regexes.extend(
                [re.compile(x) for x in stop_regex])

    def set_match_regexes(self, match_regex: Optional[List[str]] = None):
        '''Extend the Processing match regex'''
        if match_regex is not None:
            self._processing_match_regexes.extend(
                [re.compile(x) for x in match_regex])

    def set_no_match_regexes(self, no_match_regex: Optional[List[str]] = None):
        '''Extend the Processing no match regex'''
        if no_match_regex is not None:
            self._processing_no_match_regexes.extend(
                [re.compile(x) for x in no_match_regex])

    def get_data_values(self) -> List[DataValue]:
        '''Get the collected data values'''
        return self._values.get_values()

    def set_line_counter(self, counter: int):
        '''In case we are reprocessing certain lines, we can reset the counter'''
        self._line_counter = counter

    def force_process_lines(self, lines: List[str]):
        '''Forcefull process lines by overriding processing flag'''
        self.turn_on_processing()
        for line in lines:
            self.process(line)
        self.turn_off_processing()

    def slice(self, index_start: Optional[int] = None, index_end: Optional[int] = None):
        '''Remove the specified indices from data values'''
        _new_values = self.get_data_values()[index_start:index_end]
        self._values.values(_new_values).count(len(_new_values))

    # Following is for special use cases involving blurbs, a blurb is a continuous lines of data

    def get_blurbs_of_continuous_lines(self) -> List[DataBlurb]:
        '''Order the items as continues blurbs of lines'''
        line_numbers = [x.get_line() for x in self.get_data_values()]
        # TODO: Implement better grouping by itertools
        start_line_number = line_numbers[0]
        current_line_number = start_line_number
        data_blurbs: List[DataBlurb] = []
        for line_number in line_numbers[1:]:
            if line_number - current_line_number == 1:
                # This means current line number is the immediate line after last one
                current_line_number = line_number
            else:
                # It means current line number is not the immediate after the last
                # Creating a blurb of start_line:current_line
                data_blurbs.append(
                    DataBlurb().start_line(start_line_number).end_line(current_line_number))
                # Resetting the start line to the current line to search for the next
                # blurb of continuous lines
                start_line_number = line_number
            current_line_number = line_number
        # Create the blurb for the last set of continous lines and append it
        data_blurbs.append(
            DataBlurb().start_line(start_line_number).end_line(current_line_number))
        return data_blurbs

    def re_organize(self):
        '''Re organize the values and sort them according to line numbers'''
        line_to_value_map = {x.get_line(): x.get_value()
                             for x in self.get_data_values()}
        line_numbers = list(line_to_value_map.keys())
        line_numbers.sort()
        # Create a list of data value based on the line numbers
        _new_data_values = [DataValue().value(
            line_to_value_map[x]).line(x) for x in line_numbers]
        # Only updating the values since, total data count is unchanged!
        self._values.values(_new_data_values)

    def remove(self, index: int):
        '''Remove certain elements based on index'''
        try:
            self._values.get_values().pop(index)
            self._values.count(self._values.get_count() - 1)
        except IndexError:
            pass

    def remove_all(self, indices: List[int]):
        '''Remove certain elements based on index'''
        indices.sort()
        deleted = 0
        for index in indices:
            self.remove(index - deleted)
            deleted = deleted + 1

    def get_regex_processing_start(self) -> List[str]:
        '''Return the list of regex values which will 
        be used to start the processing of lines'''
        return []

    def get_regex_processing_stop(self) -> List[str]:
        '''Return the list of regex values which will 
        be used to stop the processing of lines'''
        return []

    def get_regex_line_match(self) -> List[str]:
        '''Return the list of regex values which will 
        be used to match the processing of lines'''
        return []

    def get_regex_line_no_match(self) -> List[str]:
        '''Return the list of regex values which will 
        be used to start the processing of lines'''
        return []

    def _get_regex_processing_start(self) -> List[re.Pattern[Any]]:
        '''Return the list of regex (Pattern) values which will 
        be used to start the processing of lines'''
        return self._processing_start_regexes

    def _get_regex_processing_stop(self) -> List[re.Pattern[Any]]:
        '''Return the list of regex (Pattern) values which will 
        be used to stop the processing of lines'''
        return self._processing_stop_regexes

    def _get_regex_line_match(self) -> List[re.Pattern[Any]]:
        '''Return the list of regex (Pattern) values which will 
        be used to match the processing of lines'''
        return self._processing_match_regexes

    def _get_regex_line_no_match(self) -> List[re.Pattern[Any]]:
        '''Return the list of regex (Pattern) values which will 
        be used to start the processing of lines'''
        return self._processing_no_match_regexes

    def _is_any_regex_match(self, line: str, regex_list: List[re.Pattern[Any]]) -> bool:
        '''Seeing if any of the regex is matching with that of given line'''
        for _regex_pattern in regex_list:
            if _regex_pattern.search(line) is not None:
                return True
        return False

    def pre_process_line(self, line: str) -> str:
        '''Pre process the line and return the processed line'''
        return self._pre_process_line(line)

    def fetch_data_value_from_line(self, line: str) -> DataValueType:
        '''Pre process the line and return the processed line'''
        return self._fetch_value_function(line)

    def add_line_data_to_values(self, line: str) -> bool:
        '''Add a given line data to values'''
        _value = self.fetch_data_value_from_line(self.pre_process_line(line))
        if _value:
            self._values.add_value(DataValue().
                                   value(_value).line(self.get_line_count()))
            return True
        return False
