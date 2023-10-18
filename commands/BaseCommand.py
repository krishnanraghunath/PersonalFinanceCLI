import argparse
from PersonalFinanceCLI.models.arguments.BaseArgument import BaseArgument
from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
from prettytable import PrettyTable

class BaseCommand:
    def __init__(self,arguments,cmdArguments):
        self.parser = argparse.ArgumentParser(description='Argument Parser')
        self.outputTableModel = None
        self.AddArgument(arguments)
        parsedArguments = self.parse(cmdArguments)
        for field in arguments.fields:
            if getattr(parsedArguments,field):
                getattr(arguments,field)(getattr(parsedArguments,field))
            else: 
                getattr(arguments,field)(None)

            
    
    def AddArgument(self,argument):
       if isinstance(argument,BaseArgument):
            arguments = ~argument
            for argKey in arguments:
                self.parser.add_argument("-"+argKey,**arguments[argKey])
    

    def parse(self,cmdArguments):
        arguments,known = self.parser.parse_known_args(cmdArguments)
        return arguments

    def _run(self):
        print("Override the _run command in command class")
    
    
    def tableSet(self,model,title = None,object=None):
        if self.outputTableModel == None:
            self.outputTableModel = model 
            self.table = PrettyTable()
            self.table.title = title
            if isinstance(object,BaseDBModel):
                self.table.field_names = object.GetColumnNames()
                object.setAlignment(self.table)
            else:
                self.table.field_names = model().GetColumnNames()
                model().setAlignment(self.table)
    
    def tablePut(self,data):
        if self.outputTableModel == None:
            print("The output table model is not set")
            return
        if not isinstance(data,self.outputTableModel):
            print("The provided data do not belong to the set model")
        self.table.add_row(data.GetAsRow())
    
    def tablePrint(self,object):
        print(self.table.get_string(fields=object.GetColumnNames(False)))
    
    def tableReset(self):
        self.outputTableModel = None 
        self.table.clear()

        
