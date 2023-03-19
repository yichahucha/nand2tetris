import re
import os
import sys

# 解析器


class Parser:
    def __init__(self, filePath):
        self.filePath = filePath
        self.symbolTable = SymbolTable()
        self.code = Code()

    def start(self):
        # 读取汇编指令
        assemblyCommands = self.read(self.filePath)
        # 初始化指令列表
        instructions = []
        for index, line in enumerate(assemblyCommands):
            label = self.label(line)
            if (label):
                # 把标签和要跳转的指令地址（也就是当前指令列表的长度）对应好，并加入到符号表
                # 标签不处理，标签不加入指令列表
                self.symbolTable.table[label] = len(instructions)
            else:
                # 把指令添加到指令列表
                instructions.append(line)

        # 汇编转机器码
        n = 16
        A = "0"
        C = "111"
        for index, command in enumerate(instructions):
            # 翻译A指令
            if command[0] == "@":
                symbol = command[1:]
                decimal = 0
                # A指令是数字（地址）
                if re.match(r"^\d+$", symbol):
                    decimal = int(symbol)
                # A指令是符号
                else:
                    # 去符号表查询对应的数字
                    if symbol in self.symbolTable.table:
                        decimal = self.symbolTable.table[symbol]
                    # 找不到就用 n 新生成一个，放入符号表
                    else:
                        self.symbolTable.table[symbol] = n
                        decimal = n
                        n += 1
                # 计算出A指令的二进制并替换掉汇编指令
                instructions[index] = A + self.decToBin15(decimal)
            # 翻译C指令
            else:
                dest, comp, jump = "", "", ""
                # = 号是计算指令，取编码表找到对应的编码
                if "=" in command:
                    orders = command.split("=")
                    dest = orders[0]
                    comp = orders[1]
                    jump = "null"
                # ；号是跳转指令，取编码表找到对应的编码
                elif ";" in command:
                    orders = command.split(";")
                    dest = "null"
                    comp = orders[0]
                    jump = orders[1]
                # 组合成C指令并替换掉对应的汇编指令
                instructions[index] = C + \
                    self.code.comp(comp) + self.code.dest(dest) + \
                    self.code.jump(jump)
        # 写入机器指令
        self.write(instructions)

    # 十进制转二进制，取15位
    def decToBin15(self, decimal):
        binary = bin(decimal)[2:].zfill(15)
        return binary
    
    # 指令写入文件
    def write(self, instructions):
        text = ""
        for order in instructions:
            text = text + order + "\n"
        name, ext = os.path.splitext(os.path.basename(self.filePath))
        with open(name + ".hack", "w") as file:
            file.write(text)

    # 读取汇编文件
    def read(self, name):
        with open(name, "r") as file:
            contents = file.read()
            return self.removeWhiteSpace(contents)

    # 处理空格，注释，空行，返回数组
    def removeWhiteSpace(self, text):
        text = text.replace(" ", "")
        text = re.sub(r"\/\/.*", "", text)
        return [s for s in text.split("\n") if len(s) > 0]
    
    # 获取 label 标签
    def label(self, line):
        l = re.findall(r"\((.+)\)", line)
        if l:
            return l[0]
        return ""

# 编码


class Code:
    def __init__(self):
        self.compTable = {"0_": "101010", "1_": "111111", "-1_": "111010", "D_": "001100", "A_M": "110000",
                          "!D_": "001101", "!A_!M": "110001", "-D_": "001111", "-A_-M": "110011", "D+1_": "011111",
                          "A+1_M+1": "110111", "D-1_": "001110", "A-1_M-1": "110010", "D+A_D+M": "000010", "D-A_D-M": "010011",
                          "A-D_M-D": "000111", "D&A_D&M": "000000", "D|A_D|M": "010101"}
        self.jumpTable = {"null": "000", "JGT": "001", "JEQ": "010",
                          "JGE": "011", "GLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
        self.destTable = {"null": "000", "M": "001", "D": "010",
                          "MD": "011", "A": "100", "AM": "101", "AD": "110", "AMD": "111"}

    def comp(self, s):
        for key in self.compTable:
            arr = key.split("_")
            if s in arr:
                index = arr.index(s)
                return str(index) + self.compTable[key]

    def dest(self, s):
        return self.destTable[s]

    def jump(self, s):
        return self.jumpTable[s]

# 符号表


class SymbolTable:
    def __init__(self):
        self.table = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10,
                      "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15, "SCREEN": 16384, "KBD": 24576, "SP": 0,
                      "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4}

    def add(self, key, value):
        self.table[key] = value

    def find(self, key):
        return key in self.table


def main():
    if len(sys.argv) < 2:
        raise "路径呢！！！！！！！"
    filePath = sys.argv[1]
    name, ext = os.path.splitext(os.path.basename(filePath))
    if ext != ".asm":
        raise "文件只能是 .asm 类型的"

    parser = Parser(filePath)
    parser.start()


if __name__ == "__main__":
    main()
