from PersonalFinanceCLI.models.BaseModel import BaseModel
class MongoDBQueryModel(BaseModel):
    def __init__(self):
        self.fields = [
            "gt",
            "lt",
            "regex",
            "in"
        ]        
        super().__init__(key_appender = '$')
        #.in seems to be problem as a function. removing it
        setattr(self,"In",self._function_set('_in'))
        
    
    def __invert__(self):
        value = super().__invert__()
        if value == {}:
            return None 
        return value


    
        