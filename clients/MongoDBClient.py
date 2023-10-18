from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError,BulkWriteError,PyMongoError
class MongoDBClient:

    def __init__(self,database,collection) -> None:
        '''
        TODO: Rethink the need for creating the static instance of db clinet per  connetion
         or think of a better way to share and manage connection between db client 
        '''
        self.collection = MongoClient()[database][collection]
        

    def insert_item(self,item) -> bool:
        try:
            response = self.collection.insert_one(item)
            return True
        except DuplicateKeyError as e:
            print("Duplicate Exception on writing %s"%str(item)[:100])
        except Exception as e:
            print("Exception thrown on writing %s...."%str(item)[:100])
        return False
    
    def insert_items(self,items):
        try:
            response = self.collection.insert_many(items,False)
            return True,[]
        except BulkWriteError as e:
            return False,e.details["writeErrors"]
    
    def find_item(self,item):
        try:
            response = self.collection.find_one(item)
            if response:
                return True,response 
            else:
                return False,{}
        except:
            return False,{}
        
        
    def find_items(self,item,projected_attributes):
        try:
            response = self.collection.find(item,projected_attributes)            
            if response:
                return True,response 
            else:
                return False,[]
        except:
            return False,[]
    
    def update_item(self,item,modify):
        try:
            result = self.collection.update_one(
                item,
                {"$set":modify})
            return True,result
        except PyMongoError as e:
            return False,[]



    
    
