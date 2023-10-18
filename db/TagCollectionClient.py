from PersonalFinanceCLI.models.db.TagCollectionModel import TagCollectionModel
from PersonalFinanceCLI.db.BaseDBClient import BaseDBClient
class TagCollectionClient(BaseDBClient):
    def __init__(self) -> None:
        super().__init__(TagCollectionModel)
        pass

    def addTag(self,tag):
        self.insert(tag)
    
    def getTag(self,tagName):
        return self.find_item(
            TagCollectionModel().tagName(tagName))

    def modifyTag(self,tag):
        current_item = self.getTag(tag.GettagName())
        if current_item == None:
            return False 
        return self.update_item(tag)
    
