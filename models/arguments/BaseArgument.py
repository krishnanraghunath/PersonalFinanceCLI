from PersonalFinanceCLI.models.BaseModel import BaseModel
from PersonalFinanceCLI.models.arguments.Argument import Argument,Actions
from re import compile

class BaseArgument(BaseModel):
    Keywords = ["i","s","h","-help","-showhelp",'-command']
    def __init__(self) -> None:
        if not hasattr(self,"fields"):
            self.fields = []
        if not hasattr(self,"verify"):
            self.verify = {}
        if not hasattr(self,"non_mandatory"):
            self.non_mandatory = []

        for reserved_field in filter(lambda x:x in BaseArgument.Keywords,self.fields):
            print("Reserved command \"%s\" found in the command. Remove it"%reserved_field)
            self.fields.remove(reserved_field)
        super().__init__()
        #Initialise the dest
        for field in self.fields:
            getattr(self,field)(Argument().dest(field).action(Actions.STORE))
        '''
        Ideally if a field named t1 is defined following value will be there
        CommandLine --> -t1 
        Stored variabled --> t1
        Rest all we would be able to modify
        '''
    
    def validate(self):
        for field in self.fields:
            field_value = getattr(self,'_'+field)
            if field_value == None and field not in self.non_mandatory:
                raise Exception("Mandatory value \"%s\" missing. Please see the command help using \"-s\""%field)
            if field_value != None and field in self.verify:
                if not self.verify[field](field_value):
                    raise Exception("Verification failed for field -> %s value -> %s"%(field,field_value))
    

    def validate_date_s(x):
        dateRegex = compile("^(\d\d?)/(\d\d?)/(\d{2})$")
        if isinstance(x,list):
            for d in x:
                if dateRegex.search(d) == None:
                    return False 
            return True
        else:
            return dateRegex.search(x) != None
    
    def validate_amount_s(x):
        amountRegex = compile("^(\d*)(.\d)?\d?$")
        if isinstance(x,list):
            for d in x:
                if amountRegex.search(d) == None:
                    return False 
            return True
        else:
            return amountRegex.search(x) != None       

    