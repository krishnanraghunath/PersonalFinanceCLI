from typing import Optional, List
import argparse
from PersonalFinanceCLI.models.arguments.BaseArgument import BaseArgument
from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from prettytable import PrettyTable

class BaseCommand:
    def __init__(self,arguments,cmdArguments):
        self.parser = argparse.ArgumentParser(description='Argument Parser')
        self.output_table_model = None
        self.add_argument(arguments)
        parsed_arguments = self.parse(cmdArguments)
        for field in arguments.fields:
            if getattr(parsed_arguments,field):
                getattr(arguments,field)(getattr(parsed_arguments,field))
            else: 
                getattr(arguments,field)(None)

            
    # Add an argument
    def add_argument(self, argument: BaseArgument) -> None:
        arguments = ~argument
        for argKey in arguments:
            self.parser.add_argument("-"+argKey,**arguments[argKey])
    

    def parse(self, cmdArguments: List):
        arguments, known = self.parser.parse_known_args(cmdArguments)
        return arguments

    def _run(self):
        print("Override the _run command in command class")
    
    
    def tableSet(self,model,title = None,object=None):
        if self.output_table_model == None:
            self.output_table_model = model 
            self.table = PrettyTable()
            self.table.title = title
            if isinstance(object,BaseDBModel):
                self.table.field_names = object.get_column_names()
                object.set_alignment(self.table)
            else:
                self.table.field_names = model().GetColumnNames()
                model().setAlignment(self.table)
    
    def tablePut(self,data):
        if self.output_table_model == None:
            print("The output table model is not set")
            return
        if not isinstance(data,self.output_table_model):
            print("The provided data do not belong to the set model")
        self.table.add_row(data.GetAsRow())
    
    def tablePrint(self,object):
        print(self.table.get_string(fields=object.GetColumnNames(False)))
    
    def tableReset(self):
        self.output_table_model = None 
        self.table.clear()

        
