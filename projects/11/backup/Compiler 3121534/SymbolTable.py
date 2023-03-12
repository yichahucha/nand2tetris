class SymbolTable:
    def __init__(self):
        self.classTable = []
        self.subroutineTable = []
        self.indexTable = {"STATIC":0,"FIELD":0,"ARG":0,"VAR":0}
        
    def startSubroutine(self):
        self.subroutineTable = []
        self.indexTable["ARG"] = 0
        self.indexTable["VAR"] = 0
    
    def define(self,name,type,kind):
        row = {"name":name,"type":type,"kind":kind,"index":self.indexTable[kind]}
        if (kind in ["STATIC","FIELD"]):
            self.classTable.append(row)
            self.indexTable[kind] = self.indexTable[kind]+1
        elif (kind in ["ARG","VAR"]):
            self.subroutineTable.append(row)
            self.indexTable[kind] = self.indexTable[kind]+1
        else:
            raise("未定义的类型 def define")
    
    def varCount(self,kind):
        return self.indexTable[kind]
    
    def kindOf(self,name):
        for row in self.classTable + self.subroutineTable:
            if row["name"] == name:
                return row["kind"]
        raise "kindOf error name "
        
    def typeOf(self,name):
        for row in self.classTable + self.subroutineTable:
            if row["name"] == name:
                return row["type"]
    
    def indexOf(self,name):
        for row in self.classTable + self.subroutineTable:
            if row["name"] == name:
                return row["index"]
    
# sys = SymbolTable()
# print(sys.varCount("STATIC"))

# sys.define("x","int","FIELD")
# sys.define("y","int","FIELD")
# sys.define("count","int","STATIC")
# sys.define("this","point","ARG")
# sys.define("other","int","ARG")
# sys.define("dx","int","VAR")
# sys.define("dy","int","VAR")

# # sys.startSubroutine()
# print(sys.classTable)
# print(sys.subroutineTable)

# print(sys.varCount("FIELD"))
# print(sys.varCount("STATIC"))
# print(sys.varCount("VAR"))

# print(sys.KindOf("count"))
# print(sys.KindOf("dx"))

# print(sys.TypeOf("count"))
# print(sys.TypeOf("dx"))

# print(sys.IndexOf("count"))
# print(sys.IndexOf("dx"))