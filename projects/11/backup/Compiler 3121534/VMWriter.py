class VMWriter:
    def __init__(self):
        self.VMCommands = []
    
    #(CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)
    def writePush(self,segment,index):
        command = "push {} {}".format(segment,index)
        self.VMCommands.append(command)
        
    def writePop(self,segment,index):
        command = "pop {} {}".format(segment,index)
        self.VMCommands.append(command)
    
    #(ADD, SUB, NEG,EQ, GT, LT, AND, OR, NOT)
    def writeArithmetic(self,command):
        arithmeticLogicCommands ={"+":"add","-":"sub","&amp;":"and","|":"or","=":"eq","&gt;":"gt","&lt;":"lt","--":"neg","~":"not"}
        if command == "*":
            command = "call Math.multiply 2"
        elif command == "/":
            command = "call Math.divide 2"
        else:
            command = arithmeticLogicCommands[command]
        self.VMCommands.append(command)
        
    def writeLabel(self,label):
        command = "label {}".format(label)
        self.VMCommands.append(command)
    
    def writeGoto(self,label):
        command = "goto {}".format(label)
        self.VMCommands.append(command)
    
    def writeIf(self,label):
        command = "if-goto {}".format(label)
        self.VMCommands.append(command)
    
    def writeCall(self,name,nArgs):
        command = "call {} {}".format(name,nArgs)
        self.VMCommands.append(command)
    
    def writeFunction(self, insertIndex ,name ,nLocals):   
        command = "function {} {}".format(name, nLocals)
        self.insert(insertIndex, command)
    
    def writeReturn(self):
        command = "return"
        self.VMCommands.append(command)
        
    def insert(self, index, command):
        self.VMCommands.insert(index,command)
    
    def insertIndex(self):
        return len(self.VMCommands)
    
    def output(self):
        text = ""
        for command in self.VMCommands:
            text += command + "\n"
        return text