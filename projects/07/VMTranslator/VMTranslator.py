import re
import sys
import os

class Parser:
    def __init__(self,filePath):
        self.filePath = filePath
        self.code = Code()
    
    def start(self):
        VMCommands = self.read(self.filePath)
        assemblyComands = []
        for index,line in enumerate(VMCommands):
            conmand = list(filter(lambda x: len(x) > 0, line.split(" ")))
            assemblyComand = []
            if conmand[0] in ["push","pop"]:
                assemblyComand = self.code.pp2assembly(conmand[0],conmand[1],conmand[2])
            elif conmand[0] in list(self.code.symbol.arithmeticLogicOp.keys())[:6]:
                assemblyComand = self.code.arithmetic2assembly(conmand[0])
            elif conmand[0] in list(self.code.symbol.arithmeticLogicOp.keys())[6:]:
                assemblyComand = self.code.logic2assembly(conmand[0], index)
            assemblyComands.extend(["//" + line] + assemblyComand)        
        self.write(assemblyComands)

    def write(self, commands):
        text = ""
        for command in commands:
            text = text + command + "\n"
        name, ext = os.path.splitext(os.path.basename(self.filePath))
        with open(name + ".asm", "w") as file:
            file.write(text)

    def read(self,name):
        with open(name, "r") as file:
            contents = file.read()
            return self.removeComments(contents)
        
    def removeComments(self,text):
        text = text.strip()
        text = re.sub(r"\/\/.*","",text)
        return list(filter(lambda x: len(x) > 0, text.split("\n")))
    
class Code:
    def __init__(self):
        self.symbol = Symbol()
        # push VM code to asm code
        self.pushAsmPart1 = {"constant":["@i","D=A"],
                     "local":["@i","D=A","@LCL","A=M+D","D=M"],
                     "argument":["@i","D=A","@ARG","A=M+D","D=M"],
                     "this":["@i","D=A","@THIS","A=M+D","D=M"],
                     "that":["@i","D=A","@THAT","A=M+D","D=M"],
                     "temp":["@addr","D=M"],
                     "static":["@fileName.i","D=M"],
                     "pointer":["@addr","D=M"]}
        self.pushAsmPart2 = ["@SP","A=M","M=D","@SP","M=M+1"]
        # pop VM code to asm code
        self.popAsmPart1 = {"local":["@i","D=A","@LCL","D=M+D","@TEMP","M=D"],
                     "argument":["@i","D=A","@ARG","D=M+D","@TEMP","M=D"],
                     "this":["@i","D=A","@THIS","D=M+D","@TEMP","M=D"],
                     "that":["@i","D=A","@THAT","D=M+D","@TEMP","M=D"],
                     "temp":["@addr","D=A","@TEMP","M=D"],
                     "static":["@fileName.i","D=A","@TEMP","M=D"],
                     "pointer":["@addr","D=A","@TEMP","M=D"]}
        self.popAsmPart2 = ["@SP","M=M-1","A=M","D=M","@TEMP","A=M","M=D"]
        # add/sub/and/or VM code to asm code
        self.arithmeticAsm1 = ["@SP","M=M-1","A=M","D=M"]+["@TEMP","M=D"]+["@SP","M=M-1","A=M","D=M"]+["@TEMP","D=D(OP)M"]+["@SP","A=M","M=D","@SP","M=M+1"]
        # neg/not VM code to asm code
        self.arithmeticAsm2 = ["@SP","M=M-1","A=M","D=M"]+["@SP","A=M","M=(OP)D","@SP","M=M+1"]
        # eq/lt/gt VM code to asm code
        self.logicAssembly = ["@SP","M=M-1","A=M","D=M"]+["@TEMP","M=D"]+["@SP","M=M-1","A=M","D=M"]+["@TEMP","D=D-M"]+["@TRUE","D;LOGIC"]+["@SP","A=M","M=0","@SP","M=M+1"]+["@FALSE","0;JMP"]+["(TRUE)","@SP","A=M","M=-1","@SP","M=M+1","(FALSE)"]
        
    def logic2assembly(self, logic, index):
        arithmeticStr = "_".join(self.logicAssembly)
        arithmeticStr = self.repalceMul(arithmeticStr,{"SP":self.symbol.memoryMap["SP"],"TEMP":self.symbol.memoryMap["TEMP"],"LOGIC":self.symbol.arithmeticLogicOp[logic],"TRUE":"TRUE"+str(index),"FALSE":"FALSE"+str(index)})
        return arithmeticStr.split("_")
        
    def arithmetic2assembly(self, operator):
        arithmeticAssembly = self.arithmeticAsm1 if operator in list(self.symbol.arithmeticLogicOp.keys())[:4] else self.arithmeticAsm2
        arithmeticStr = "_".join(arithmeticAssembly)
        arithmeticStr = self.repalceMul(arithmeticStr,{"SP":self.symbol.memoryMap["SP"],"TEMP":self.symbol.memoryMap["TEMP"],"(OP)":self.symbol.arithmeticLogicOp[operator]})
        return arithmeticStr.split("_")
    
    def pp2assembly(self, command, segment, i):
        ppAssembly = []
        if command == "push":
            ppAssembly = self.pushAsmPart1[segment] + self.pushAsmPart2
        else:
            ppAssembly = self.popAsmPart1[segment] + self.popAsmPart2
        assemblyStr = "_".join(ppAssembly)
        if segment == "constant":
            assemblyStr = self.repalceMul(assemblyStr,{"i":i})
        elif segment == "local":
            assemblyStr = self.repalceMul(assemblyStr,{"i":i,"LCL":self.symbol.memoryMap["LCL"],"TEMP":self.symbol.memoryMap["TEMP"]})
        elif segment == "argument":
            assemblyStr = self.repalceMul(assemblyStr,{"i":i,"ARG":self.symbol.memoryMap["ARG"],"TEMP":self.symbol.memoryMap["TEMP"]})
        elif segment == "this":
            assemblyStr = self.repalceMul(assemblyStr,{"i":i,"THIS":self.symbol.memoryMap["THIS"],"TEMP":self.symbol.memoryMap["TEMP"]})
        elif segment == "that":
            assemblyStr = self.repalceMul(assemblyStr,{"i":i,"THAT":self.symbol.memoryMap["THAT"],"TEMP":self.symbol.memoryMap["TEMP"]})
        elif segment == "temp":
            assemblyStr = self.repalceMul(assemblyStr,{"addr":str(int(self.symbol.memoryMap["TEMP"])+int(i)),"TEMP":self.symbol.memoryMap["TEMP"]})
        elif segment == "static":
            assemblyStr = self.repalceMul(assemblyStr,{"fileName":fileName,"i":i,"TEMP":self.symbol.memoryMap["TEMP"]})
        elif segment == "pointer":
            assemblyStr = self.repalceMul(assemblyStr,{"addr":self.symbol.memoryMap["THIS"] if i == "0" else self.symbol.memoryMap["THAT"], "TEMP":self.symbol.memoryMap["TEMP"]})
        else:
            return []
        return assemblyStr.split("_")
        
    def repalceMul(self, text, replacements):
        # 构造正则表达式模式，用于匹配替换的字符串
        pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
        # 使用 re.sub() 函数和正则表达式模式，同时替换多个子字符串
        result = pattern.sub(lambda m: replacements[m.group(0)], text)
        return result
    
class Symbol:
    def __init__(self):
        self.memoryMap = {"SP":"0","LCL":"1","ARG":"2","THIS":"3","THAT":"4","TEMP":"5"}
        self.arithmeticLogicOp ={"add":"+","sub":"-","and":"&","or":"|","neg":"-","not":"!","eq":"JEQ","gt":"JGT","lt":"JLT"}
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise "path?.........."
    filePath = sys.argv[1]
    fileName, ext = os.path.splitext(os.path.basename(filePath))
    if ext != ".vm":
        raise ".vm must........."
    
    Parser(filePath).start()
    