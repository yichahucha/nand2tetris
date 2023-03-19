class SymbolTable:
    def __init__(self):
        self.classTable = []
        self.subroutineTable = []
        self.indexTable = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def startSubroutine(self):
        self.subroutineTable = []
        self.indexTable["ARG"] = 0
        self.indexTable["VAR"] = 0

    def define(self, name, type, kind):
        row = {"name": name, "type": type, "kind": kind,
               "index": self.indexTable[kind]}
        if (kind in ["STATIC", "FIELD"]):
            self.classTable.append(row)
            self.indexTable[kind] = self.indexTable[kind]+1
        elif (kind in ["ARG", "VAR"]):
            self.subroutineTable.append(row)
            self.indexTable[kind] = self.indexTable[kind]+1
        else:
            raise ValueError("未定义的类型 {}".format(kind))

    def varCount(self, kind):
        return self.indexTable[kind]

    def kindOf(self, name):
        for row in self.classTable + self.subroutineTable:
            if row["name"] == name:
                return row["kind"]
        raise ValueError("kindOf error name {}".format(name))

    def typeOf(self, name):
        for row in self.classTable + self.subroutineTable:
            if row["name"] == name:
                return row["type"]

    def indexOf(self, name):
        for row in self.classTable + self.subroutineTable:
            if row["name"] == name:
                return row["index"]
