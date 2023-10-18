from PersonalFinanceCLI.models.BaseModel import BaseModel
from hashlib import md5
from functools import reduce

class BaseDBModel(BaseModel):
    def MD5Hash(hashfunction):
        def MD5Hash(self):
            return md5(hashfunction(self).encode("utf-8")).hexdigest()
        return MD5Hash

    def __init__(self,no_transforms=False) -> None:
        #Add the id fields
        self.fields.append('_id')
        self.fields.append('_error_code')
        if no_transforms:
            self.transforms = {}
        super().__init__()
    
    @MD5Hash
    def hash(self):
        #Just returing the hash using primary keys
        try:
            fieldsVals = ~self
            hashF = reduce(lambda x,y: x + y,list(map(lambda x:str(fieldsVals[x]),self.hashfields)))
            return hashF
        except:
            import traceback
            traceback.print_exc()
            raise Exception("Object -> %s,Primary Keys -> (%s)  ==> are not defined properly"%
                            (str(~self),",".join(self.hashfields)))
    
    def GetHashFields(self):
        return self.hashfields
    
    def GetColumnNames(self,includeAll = True):
        columns = []
        for x in self.fields:
            if  includeAll == True and x in self.printtable:
                columns.append(self.printtable[x])
            if includeAll == False and  x in self.printtable and self._function_get('_' + x)() !=None :
                columns.append(self.printtable[x])
        return columns
    
    def GetAsRow(self):
        rowvals = []
        for x in self.fields:
            if x not in self.printtable:
                continue
            try:
                if not getattr(self,'_'+x) is None:
                    if x in self.printfunc:
                        rowvals.append(self.printfunc[x](getattr(self,'_'+x)))
                    elif isinstance(getattr(self,'_'+x),BaseDBModel):
                        rowvals.append(getattr(self,'_'+x).PrettyString())
                    else:
                        rowvals.append(getattr(self,'_'+x))
                else:
                    rowvals.append('')
            except:
                rowvals.append('')
        return rowvals

    def setAlignment(self,table):
        pass

    def PrettyString(self):
        return ~self
    


