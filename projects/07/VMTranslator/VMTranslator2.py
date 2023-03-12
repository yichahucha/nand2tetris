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
            if conmand[0] in self.code.symbol.memoryAccessComamands:
                assemblyComand = self.code.pushPop2assembly(conmand[0],conmand[1],conmand[2])
            elif conmand[0] in list(self.code.symbol.arithmeticLogicCommands.keys()):
                assemblyComand = self.code.arithmeticLogic2assembly(conmand[0], index)
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
                     "temp":["@ADDR","D=M"],
                     "static":["@FILENAME.i","D=M"],
                     "pointer":["@ADDR","D=M"]}
        self.pushAsmPart2 = ["@SP","A=M","M=D","@SP","M=M+1"]
        # pop VM code to asm code
        self.popAsmPart1 = {"local":["@i","D=A","@LCL","D=M+D","@R13","M=D"],
                     "argument":["@i","D=A","@ARG","D=M+D","@R13","M=D"],
                     "this":["@i","D=A","@THIS","D=M+D","@R13","M=D"],
                     "that":["@i","D=A","@THAT","D=M+D","@R13","M=D"],
                     "temp":["@ADDR","D=A","@R13","M=D"],
                     "static":["@FILENAME.i","D=A","@R13","M=D"],
                     "pointer":["@ADDR","D=A","@R13","M=D"]}
        self.popAsmPart2 = ["@SP","M=M-1","A=M","D=M","@R13","A=M","M=D"]
        # add/sub/and/or VM code to asm code
        self.arithmeticAsm1 = ["@SP","M=M-1","A=M","D=M"]+["@R13","M=D"]+["@SP","M=M-1","A=M","D=M"]+["@R13","D=D(OP)M"]+["@SP","A=M","M=D","@SP","M=M+1"]
        # neg/not VM code to asm code
        self.arithmeticAsm2 = ["@SP","M=M-1","A=M","D=M"]+["@SP","A=M","M=(OP)D","@SP","M=M+1"]
        # eq/lt/gt VM code to asm code
        self.logicAsm = ["@SP","M=M-1","A=M","D=M"]+["@R13","M=D"]+["@SP","M=M-1","A=M","D=M"]+["@R13","D=D-M"]+["@TRUE","D;LOGIC"]+["@SP","A=M","M=0","@SP","M=M+1"]+["@FALSE","0;JMP"]+["(TRUE)","@SP","A=M","M=-1","@SP","M=M+1","(FALSE)"]
        
    def arithmeticLogic2assembly(self, op, index):
        asm = []
        arithmeticLogicCommands = list(self.symbol.arithmeticLogicCommands.keys())
        # add/sub/and/or
        if op in arithmeticLogicCommands[:4]:
            asm = self.arithmeticAsm1
        # neg/not
        elif op in arithmeticLogicCommands[4:6]:
            asm = self.arithmeticAsm2
        # eq/lt/gt
        else:
            asm = self.logicAsm
        asmStr = "_".join(asm)
        if op in arithmeticLogicCommands[:6]:
            asmStr = self.repalceMul(asmStr,{"(OP)":self.symbol.arithmeticLogicCommands[op]})
        else:
            asmStr = self.repalceMul(asmStr,{"LOGIC":self.symbol.arithmeticLogicCommands[op],"TRUE":"TRUE"+str(index),"FALSE":"FALSE"+str(index)})
        return asmStr.split("_")
    
    def pushPop2assembly(self, command, segment, i):
        asm = []
        # push
        if command == self.symbol.memoryAccessComamands[0]:
            asm = self.pushAsmPart1[segment] + self.pushAsmPart2
        # pop
        else:
            asm = self.popAsmPart1[segment] + self.popAsmPart2
        asmStr = "_".join(asm)
        if segment == "constant" or segment == "local" or segment == "argument" or segment == "this" or segment == "that":
            asmStr = self.repalceMul(asmStr,{"i":i})
        elif segment == "temp":
            asmStr = self.repalceMul(asmStr,{"ADDR":str(5+int(i))})
        elif segment == "static":
            asmStr = self.repalceMul(asmStr,{"FILENAME":fileName,"i":i})
        elif segment == "pointer":
            asmStr = self.repalceMul(asmStr,{"ADDR": "THIS" if i == "0" else "THAT"})
        else:
            return []
        return asmStr.split("_")
        
    def repalceMul(self, text, replacements):
        # 构造正则表达式模式，用于匹配替换的字符串
        pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
        # 使用 re.sub() 函数和正则表达式模式，同时替换多个子字符串
        result = pattern.sub(lambda m: replacements[m.group(0)], text)
        return result
    
class Symbol:
    def __init__(self):
        #{"SP":"0","LCL":"1","ARG":"2","THIS":"3","THAT":"4","TEMP":"5"}
        self.arithmeticLogicCommands ={"add":"+","sub":"-","and":"&","or":"|","neg":"-","not":"!","eq":"JEQ","gt":"JGT","lt":"JLT"}
        self.memoryAccessComamands = ["push","pop"]
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise "path?.........."
    filePath = sys.argv[1]
    fileName, ext = os.path.splitext(os.path.basename(filePath))
    if ext != ".vm":
        raise ".vm must........."
    
    Parser(filePath).start()
    