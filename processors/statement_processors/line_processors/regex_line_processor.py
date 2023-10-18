
import re
from PersonalFinanceCLI.models.transactions.DataValue import DataValue
from PersonalFinanceCLI.models.transactions.DataValues import DataValues
from PersonalFinanceCLI.models.transactions.DataBlurb import DataBlurb
'''
Line Processor based on Regex on only for following single purpose
1 -> For a series of inputs
2 -> Decide when processor should get activated based on start regexes 
3 -> See if the values are according to the format if it is activated based on match regex
4 -> Decide when processor should get deactivated based on stop egex
'''
class RegexLineProcessor:
    def __init__(self):
        self.__processing_start_regexes = []
        self.__processing_stop_regexes = []
        self.__processing_match_regexes = []
        self.__processing_no_match_regexes = []
        self._processing = False
        self._processing_start_regexes = []
        self._processing_stop_regexes = []
        self._processing_match_regexes = []
        self._processing_no_match_regexes = []
        self._fetch_value_function = None
        self._pre_process_line = None
        self._counter = 0
        self._values = DataValues().values([]).count(0)
        self.initialised = False
        pass

    def initialise(self):
        self.initialised = True
        #All the regexes will be used with OR combination, i.e if any of hte regex in a list matches that would be fine
        self._processing_start_regexes = list(map(lambda y:re.compile(y),self.__processing_start_regexes))
        self._processing_stop_regexes = list(map(lambda y: re.compile(y), self.__processing_stop_regexes))
        self._processing_match_regexes = list(map(lambda y: re.compile(y), self.__processing_match_regexes))
        self._processing_no_match_regexes = list(map(lambda y: re.compile(y), self.__processing_no_match_regexes))

    def process(self,line):
        if self.initialised ==False:
            raise Exception('Regex Processor is not initialised.')
        self._counter = self._counter + 1
        line = line.strip()
        for stop_regex in self._processing_stop_regexes:
            if stop_regex.search(line):
                self._processing =  False
                return False
        if self._processing:
            if len(list(filter(lambda y:y.search(line)!=None,self._processing_no_match_regexes))) > 0:
                return False
            for match_regex in self._processing_match_regexes:
                if match_regex.search(line):
                    if self._pre_process_line:
                        line = self._pre_process_line(line)
                    _value = self._fetch_value_function(line)
                    if _value:
                        counter = self._values.Getcount() + 1
                        self._values.Getvalues().append(DataValue() \
                                                                .value(_value)\
                                                                .line(self._counter))
                        self._values.count(counter)
                        return True
                    return False

        for start_regex in self._processing_start_regexes:
            if start_regex.search(line):
                self._processing = True
                return False

    def GetTotalLinesProcessed(self):
        return self._counter

    def GetTotalValues(self):
        return self._values.Getcount()

    def SetFetchFunction(self,function):
        self._fetch_value_function = function

    def SetPreProcessFunction(self,function):
        self._pre_process_line = function


    def set_start_regexes(self,start_regex = []):
        self.__processing_start_regexes.extend(start_regex)
        self.initialise()

    def set_stop_regexes(self,stop_regex = []):
        self.__processing_stop_regexes.extend(stop_regex)
        self.initialise()

    def set_match_regexes(self,match_regex = []):
        self.__processing_match_regexes.extend(match_regex)
        self.initialise()

    def set_no_match_regexes(self,no_match_regex = []):
        self.__processing_no_match_regexes.extend(no_match_regex)
        self.initialise()

    def GetValues(self):
        return self._values.Getvalues()

    '''In case we are reprocessing certain lines, we can reset the counter'''
    def SetLineCounter(self,counter):
        self._counter = counter 

    #Overriding the start checks only.
    def OverrideAndProcess(self,lines):
        self._processing = True 
        for line in lines:
            self.process(line)
        self._processing = False


    #Remove specified indices
    def slice(self,indexS,indexE=None):
        case_identifier = str(indexS!=None)[0]+str(indexE!=None)[0]
        new_values = []
        if case_identifier == "TT":
             new_values.extend(self.GetValues()[indexS:indexE])
        if case_identifier == "TF":
             new_values.extend(self.GetValues()[indexS:])
        if case_identifier == "FT":
             new_values.extend(self.GetValues()[:indexE])
        self._values.values(new_values)
        self._values.count(len(new_values))

    #Following is for special use cases involving blurbs, a blurb is a continuus lines of data
    '''Order the items as continues blurbs of lines'''
    def blurbs(self):
        lines = list(map(lambda y:y.Getline(),self._values.Getvalues()))
        #TODO: Implement better grouping by itertools
        startLine = lines[0]
        currentLine = startLine
        blurbs = []
        for line in lines[1:]:
            if line - currentLine == 1:
                currentLine = line
            else:
                blurbs.append(
                    DataBlurb().startLine(startLine).endLine(currentLine))
                startLine = line     
            currentLine = line  
        blurbs.append(
                    DataBlurb().startLine(startLine).endLine(currentLine))
        return blurbs
    
    '''Re organize the values and sort them according to line nunbmers'''
    def re_organize(self):
        line_to_value_map = {x.Getline():x.Getvalue() for x in self.GetValues()}
        line_numbers = list(line_to_value_map.keys())
        line_numbers.sort()
        _new_values = DataValues().values([]).count(0)
        [_new_values.Getvalues().append(DataValue().value(line_to_value_map[x]).line(x)) for x in line_numbers]
        _new_values.count(len(line_numbers))
        self._values = _new_values
    
    '''Remove certain elements based on index'''
    def remove(self,index):
        try:
            self._values.Getvalues().pop(index)
            self._values.count(self._values.Getcount() - 1)
        except IndexError as e:
            pass

    '''Remove certain elements based on index'''
    def removeAll(self,indices):
        indices.sort()
        deleted = 0
        for index in indices:
            self.remove(index - deleted)
            deleted = deleted + 1
            
  