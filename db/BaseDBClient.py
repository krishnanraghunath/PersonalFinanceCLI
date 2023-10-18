from PersonalFinanceCLI.clients.MongoDBClient import MongoDBClient
from PersonalFinanceCLI.models.db.BaseDBModel import BaseDBModel
class BaseDBClient:
    #DatabaseName = "test"
    DatabaseName = "prod"
    def __init__(self,collectionModel) -> None:
        self.model = collectionModel
        self.client = MongoDBClient(BaseDBClient.DatabaseName,collectionModel.CollectionName)

    def insert(self,item):
        '''
        Create an id fields
        '''
        item = item._id(item.hash())
        return self.client.insert_item(~item)

    def insert_all(self,items):
        '''
        Create an id fields
        '''
        items = list(map(lambda x:~x._id(x.hash()),items))
        return self.client.insert_items(items)

    
    def find_item(self,item):
        '''
        Find a single item if present
        '''
        response,item = self.client.find_item(~item)
        if response:
            return self.model().ingest(item)
        return None

        
    def find_items(self,item,projected_values,sorters = None):
        sortings = []
        if sorters and isinstance(sorters,list):
            for i in sorters:
                if isinstance(i,BaseDBModel):
                    i = ~i
                    if len(i) == 1:
                        sortings.append([(x,i[x]) for x in i][0])

        '''
        Find a single item if present
        '''
        response,items = self.client.find_items(~item,~projected_values)
        if response:
            if sorters:
                return [self.model().ingest(x) for x in items.sort(sortings)]
            return[self.model().ingest(x) for x in items]
        return None
    
    def update_item(self,modifiedItem):
        queryItem = self.model()._id(modifiedItem.hash())
        #Not modifying hash fields
        modifiedItem._id(None)
        for hashField in self.model().GetHashFields():
            getattr(modifiedItem,hashField)(None)
        result,response = self.client.update_item(~queryItem,~modifiedItem)
        if result:
            if response.matched_count == 1 and response.modified_count == 1:
                return True 
            if response.matched_count == 0:
                print("Unable to find matching entries for item: %s on colleciton %s "%(~queryItem,self.model.CollectionName))
                return False
        return True





