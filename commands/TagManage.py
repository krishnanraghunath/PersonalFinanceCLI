from PersonalFinanceCLI.models.arguments.TagManagementArgument import TagManagementArgument
from PersonalFinanceCLI.commands.BaseCommand import BaseCommand
from PersonalFinanceCLI.models.db.TagRuleModel import TagRuleModel
from PersonalFinanceCLI.models.db.TagCollectionModel import TagCollectionModel
from PersonalFinanceCLI.db.TagCollectionClient import TagCollectionClient

class TagManage(BaseCommand):
    def __init__(self,cmdLineArgs):
        self.arguments = TagManagementArgument()
        super().__init__(self.arguments,cmdLineArgs)
        self.arguments.validate()
        self.tagCollectionClient = TagCollectionClient()

    def _run(self):
        tagCollection = TagCollectionModel().tagName(self.arguments.GettagName())\
                            .accountNumbers(self.arguments.GetaccountNumber()) \
                            .rules( 
                                    TagRuleModel()
                                        .amountMin(self.arguments.Getamountgt()) 
                                        .amountMax(self.arguments.Getamountlt()) 
                                        .dateFrom(self.arguments.GetfromDate()) 
                                        .dateTo(self.arguments.GettoDate()) 
                                        .descriptionRegex(self.arguments.GetdescriptionRegex()))
        
        if self.arguments.Getmodify():
            self.tagCollectionClient.modifyTag(tagCollection)
            return 
        
        self.tagCollectionClient.addTag(tagCollection)
    

      