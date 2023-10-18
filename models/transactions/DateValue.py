from PersonalFinanceCLI.models.BaseModel import BaseModel
from datetime import datetime
from re import compile 

class DateValue(BaseModel):
    def __init__(self):
        self.transforms = {
            "date" : lambda x:DateValue.DateToString(x)
        }
        self.fields = [
            "date"
        ]
        super().__init__()
    
    def DateToString(date):
        try:
            return datetime.fromtimestamp(date/1000).strftime('%d-%m-%Y')
        except:
            return None
    
    def DDMMYYToTimestamp(date):
        dateRegex = compile("^(\d\d?)/(\d\d?)/(\d{2})$")
        try:
            dd,mm,yy = dateRegex.findall(date)[0]
            return datetime(year=int(yy)+2000, month=int(mm), day=int(dd)).timestamp()*1000
        except:
            '''If it is already a time stamp return it'''
            try:
                #100 years of me!! 
                if int(date) > 640580700000 and int(date) < 3796340700000:
                    return int(date)
            except:
                pass
        return None

    


    
        