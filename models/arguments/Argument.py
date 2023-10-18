from PersonalFinanceCLI.models.BaseModel import BaseModel

class Argument(BaseModel):
    def __init__(self) -> None:
        self.fields = [
            "action",
            "choices",
            "const",
            "default",
            "dest",
            "help",
            "metavar",
            "nargs",
            "required",
            "type"
            ]
        super().__init__()


class Actions:
    STORE = "store"
    STORE_CONSTANT = "store_const"
    STORE_TRUE = "store_true"
    APPEND = "append"
    APPEND_CONSTANT = "append_const"
    COUNT = "count"
    HELP = "help"
    VERSION = "version"


