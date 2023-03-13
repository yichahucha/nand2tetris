import glob
import re
import sys
import os


class Parser:
    def __init__(self, filePath):
        self.code = Code()
        self.filePath = filePath

        if os.path.isdir(filePath):  # 判断路径是否为文件夹
            vm_files = glob.glob(os.path.join(
                filePath, '*.vm'))  # 获取该文件夹下的所有.vm文件
        else:  # 如果是.vm文件，则直接使用该文件
            vm_files = [filePath]

        allCommands = []
        # 如果是文件夹添加初始化代码
        if os.path.isdir(filePath):
            allCommands.extend(self.code.writeInit())
        for file in vm_files:
            baseName = os.path.basename(file)
            fileName, ext = os.path.splitext(baseName)
            asmCommands = self.start(file, fileName)
            allCommands.extend(["//"+baseName] + asmCommands)
        self.write(allCommands)

    def start(self, file, fileName):
        VMCommands = self.read(file)
        self.code.writeFileName(fileName)
        assemblyComands = []
        for index, line in enumerate(VMCommands):
            conmand = list(filter(lambda x: len(x) > 0, line.split(" ")))
            assemblyComand = []
            if conmand[0] in self.code.symbol.memoryAccessComamands:
                assemblyComand = self.code.pushPop2assembly(
                    conmand[0], conmand[1], conmand[2])
            elif conmand[0] in list(self.code.symbol.arithmeticLogicCommands.keys()):
                assemblyComand = self.code.arithmeticLogic2assembly(
                    conmand[0], index)
            elif conmand[0] in self.code.symbol.branchingComamands:
                assemblyComand = self.code.branching2assembly(
                    conmand[0], conmand[1])
            elif conmand[0] == "function":
                assemblyComand = self.code.writeFunction(
                    conmand[1], conmand[2])
            elif conmand[0] == "call":
                assemblyComand = self.code.writeCall(
                    conmand[1], conmand[2], index)
            elif conmand[0] == "return":
                assemblyComand = self.code.writeReturn()
            assemblyComands.extend(["//" + line] + assemblyComand)
        return assemblyComands

    def write(self, commands):
        text = ""
        for command in commands:
            text = text + command + "\n"
        fileName = ""
        dirName = ""
        if os.path.isdir(filePath):
            fileName = os.path.basename(filePath)
            dirName = filePath
        else:
            name, ext = os.path.splitext(os.path.basename(self.filePath))
            fileName = name
            dirName = os.path.dirname(filePath)
        with open(dirName + "/" + fileName + ".asm", "w") as file:
            file.write(text)

    def read(self, name):
        with open(name, "r") as file:
            contents = file.read()
            return self.removeComments(contents)

    def removeComments(self, text):
        text = text.strip()
        text = re.sub(r"\/\/.*", "", text)
        return list(filter(lambda x: len(x) > 0, text.split("\n")))


class Code:
    def __init__(self):
        self.symbol = Symbol()
        self.funcName = ""
        # push VM code to asm code
        self.pushAsmPart1 = {"constant": ["@i", "D=A"],
                             "local": ["@i", "D=A", "@LCL", "A=M+D", "D=M"],
                             "argument": ["@i", "D=A", "@ARG", "A=M+D", "D=M"],
                             "this": ["@i", "D=A", "@THIS", "A=M+D", "D=M"],
                             "that": ["@i", "D=A", "@THAT", "A=M+D", "D=M"],
                             "temp": ["@ADDR", "D=M"],
                             "static": ["@FILENAME.i", "D=M"],
                             "pointer": ["@ADDR", "D=M"]}
        self.pushAsmPart2 = ["@SP", "A=M", "M=D", "@SP", "M=M+1"]
        # pop VM code to asm code
        self.popAsmPart1 = {"local": ["@i", "D=A", "@LCL", "D=M+D", "@R13", "M=D"],
                            "argument": ["@i", "D=A", "@ARG", "D=M+D", "@R13", "M=D"],
                            "this": ["@i", "D=A", "@THIS", "D=M+D", "@R13", "M=D"],
                            "that": ["@i", "D=A", "@THAT", "D=M+D", "@R13", "M=D"],
                            "temp": ["@ADDR", "D=A", "@R13", "M=D"],
                            "static": ["@FILENAME.i", "D=A", "@R13", "M=D"],
                            "pointer": ["@ADDR", "D=A", "@R13", "M=D"]}
        self.popAsmPart2 = ["@SP", "M=M-1", "A=M", "D=M", "@R13", "A=M", "M=D"]
        # add/sub/and/or VM code to asm code
        self.arithmeticAsm1 = ["@SP", "M=M-1", "A=M", "D=M"]+["@R13", "M=D"]+[
            "@SP", "M=M-1", "A=M", "D=M"]+["@R13", "D=D(OP)M"]+["@SP", "A=M", "M=D", "@SP", "M=M+1"]
        # neg/not VM code to asm code
        self.arithmeticAsm2 = ["@SP", "M=M-1", "A=M",
                               "D=M"]+["@SP", "A=M", "M=(OP)D", "@SP", "M=M+1"]
        # eq/lt/gt VM code to asm code
        self.logicAsm = ["@SP", "M=M-1", "A=M", "D=M"]+["@R13", "M=D"]+["@SP", "M=M-1", "A=M", "D=M"]+["@R13", "D=D-M"]+["@TRUE",
                                                                                                                         "D;LOGIC"]+["@SP", "A=M", "M=0", "@SP", "M=M+1"]+["@FALSE", "0;JMP"]+["(TRUE)", "@SP", "A=M", "M=-1", "@SP", "M=M+1", "(FALSE)"]

    def arithmeticLogic2assembly(self, op, index):
        asm = []
        arithmeticLogicCommands = list(
            self.symbol.arithmeticLogicCommands.keys())
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
            asmStr = self.repalceMul(
                asmStr, {"(OP)": self.symbol.arithmeticLogicCommands[op]})
        else:
            asmStr = self.repalceMul(asmStr, {
                                     "LOGIC": self.symbol.arithmeticLogicCommands[op], "TRUE": "TRUE"+str(index), "FALSE": "FALSE"+str(index)})
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
            asmStr = self.repalceMul(asmStr, {"i": i})
        elif segment == "temp":
            asmStr = self.repalceMul(asmStr, {"ADDR": str(5+int(i))})
        elif segment == "static":
            asmStr = self.repalceMul(
                asmStr, {"FILENAME": self.fileName, "i": i})
        elif segment == "pointer":
            asmStr = self.repalceMul(
                asmStr, {"ADDR": "THIS" if i == "0" else "THAT"})
        else:
            return []
        return asmStr.split("_")

    def writeFileName(self, name):
        self.fileName = name

    def branching2assembly(self, command, label):
        if command == self.symbol.branchingComamands[0]:
            return self.writeLabel(label)
        elif command == self.symbol.branchingComamands[1]:
            return self.writeGoTo(label)
        else:
            return self.writeIf(label)

    def writeLabel(self, label):
        return ["({}${})".format(self.funcName, label)]

    def writeGoTo(self, label):
        return ["@{}${}".format(self.funcName, label), "0;JMP"]

    def writeIf(self, label):
        return ["@SP", "M=M-1", "A=M", "D=M"] + ["@{}${}".format(self.funcName, label), "D;JNE"]

    def writeFunction(self, name, nVars):
        self.funcName = name
        arr = []
        for _ in range(int(nVars)):
            arr.extend(self.pushPop2assembly("push", "constant", "0"))
        return ["({})".format(name)] + arr

    def writeReturn(self):
        return sum([["@LCL", "D=M", "@R15", "M=D"],  # put LCL into R15
                    ["@5", "D=A", "@R15", "A=M-D", "D=M", "@R14", "M=D"],  # put retAddr into R14
                    ["@SP", "AM=M-1", "D=M", "@ARG", "A=M", "M=D"],  # *ARG=pop()
                    ["@ARG", "D=M+1", "@SP", "M=D"],  # SP=ARG+1
                    ["@R15", "A=M-1", "D=M", "@THAT", "M=D"],  # THAT=*(FRAME-1)
                    ["@2", "D=A", "@R15", "A=M-D", "D=M", "@THIS", "M=D"],  # THIS=*(FRAME-2)
                    ["@3", "D=A", "@R15", "A=M-D", "D=M", "@ARG", "M=D"],  # ARG=*(FRAME-3)
                    ["@4", "D=A", "@R15", "A=M-D", "D=M", "@LCL", "M=D"],  # LCL=*(FRAME-4)
                    ["@R14", "A=M", "0;JMP"]  # goto retAddr
                    ], [])

    def writeCall(self, name, nArgs, index):
        returnLabel = name + "$ret." + str(index)
        return ["@"+returnLabel, "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # push retAddr
                "@LCL", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # 存入当前LCL值
                "@ARG", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # 存入当前ARG值
                "@THIS", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # 存入当前THIS值
                "@THAT", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # 存入当前THAT值
                "@"+str(int(nArgs)+5), "D=A", "@SP", "D=M-D", "@ARG", "M=D", # 设置ARG
                "@SP", "D=M", "@LCL", "M=D",  # 设置LCL
                "@"+name, "0;JMP",  # 跳转函数
                "({})".format(returnLabel)  # 返回标签
                ]

    def writeInit(self):
        return sum([["@256", "D=A", "@SP", "M=D"], self.writeCall("Sys.init", "0", 0)], [])

    def repalceMul(self, text, replacements):
        pattern = re.compile("|".join(re.escape(k)
                             for k in replacements.keys()))
        result = pattern.sub(lambda m: replacements[m.group(0)], text)
        return result


class Symbol:
    def __init__(self):
        # {"SP":"0","LCL":"1","ARG":"2","THIS":"3","THAT":"4","TEMP":"5"}
        self.arithmeticLogicCommands = {"add": "+", "sub": "-", "and": "&",
                                        "or": "|", "neg": "-", "not": "!", "eq": "JEQ", "gt": "JGT", "lt": "JLT"}
        self.memoryAccessComamands = ["push", "pop"]
        self.branchingComamands = ["label", "goto", "if-goto"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise "path?.........."

    filePath = sys.argv[1]
    Parser(filePath)
