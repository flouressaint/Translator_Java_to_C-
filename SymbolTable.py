class SymbolTable:
    # В таблице символов хранятся пары: id и type
    def __init__(self):
        self.table = dict()

    def isExist(self, _id) -> bool:
        if _id in self.table.keys():
            return True
        else:
            return False
