import re, os
import xml.dom.minidom
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

class CompilationEngine:
    def __init__(self, file):
        
        self.file = file
        self.out_puts = []
        self.tokenizer = JackTokenizer(file)
        self.current_token = self.tokenizer.next()
        
        self.className = ""
        self.whileLabelIndex = 0
        self.ifLabelIndex = 0
        self.symbolTable = SymbolTable()
        self.vmWriter = VMWriter()
        self.compileClass()
    
    # 检验当前token和语法规则是否匹配
    def eat(self, tokens):
        if self.current_token_text in tokens:
            self.advance()
        else:
            print("ERROR: current_token_text {} tokens{}".format(self.current_token_text,tokens))
        
    # 添加到新的输出 并取出下一个 token
    def advance(self):
        if self.current_token:
            self.out_puts.append(self.current_token)
        self.current_token = self.tokenizer.next()
        
    # class: 'class' className '{' classVarDec* subroutineDec* '}'
    def compileClass(self):
        self.out_puts.append("<class>")
        self.eat(["class"])
        ###
        self.className = self.current_token_text
        ###
        # className
        self.advance()
        self.eat(["{"])
        # classVarDec*
        while self.current_token_text in ["static","field"]:
            self.compileClassVarDec()
        # subroutineDec*
        while self.current_token_text in ["constructor","function","method"]:
            self.compileSubroutineDec()
        self.eat(["}"])
        self.out_puts.append("</class>")
        
    # classVarDec: ('static'|'field') type varName (', ' varName)* ';'
    # type: 'int' | 'char' | 'boolean' | className
    def compileClassVarDec(self):
        self.out_puts.append("<classVarDec>")
        ###
        kind = self.current_token_text
        ###
        # ('static'|'field')
        self.eat(["static","field"])
        ###
        type = self.current_token_text
        ###
        # type
        self.advance()
        ###
        name = self.current_token_text
        self.symbolTable.define(name, type, kind)
        ###
        # varName
        self.advance()
        # (','varName)*
        if self.current_token_text == ",":
            while self.current_token_text != ";":
                self.eat([","])
                name = self.current_token_text
                self.symbolTable.define(name, type, kind)
                self.advance()
        self.eat([";"])
        self.out_puts.append("</classVarDec>")
        
    # subroutineDec: ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody
    def compileSubroutineDec(self):
        self.out_puts.append("<subroutineDec>")
        ###
        self.symbolTable.startSubroutine()
        self.whileLabelIndex = 0
        self.ifLabelIndex = 0
        ###
        ###
        subroutineType = self.current_token_text
        ###
        self.eat(["constructor","function","method"])
        # ('void'|type)
        self.advance()
        ###
        subroutineName = self.current_token_text
        ###
        # subroutineName
        self.advance()
        self.eat(["("])
        self.compileParameterList(subroutineType)
        self.eat([")"])
        ###
        ii = self.vmWriter.insertIndex()
        ###
        self.compileSubroutineBody(subroutineType)
        ###
        self.vmWriter.writeFunction(ii, "{}.{}".format(self.className, subroutineName), self.symbolTable.varCount("local"))
        ###
        self.out_puts.append("</subroutineDec>")
    
    # parameterList: ((type varName) (',' type varName)*)?
    def compileParameterList(self, subroutineType):
        self.out_puts.append("<parameterList>")
        ###
        if subroutineType == "method":
            self.symbolTable.define("this", self.className, "argument")
        ###
        if self.current_token_text != ")":
            ###
            type = self.current_token_text
            ###
            #type
            self.advance()
            ###
            name = self.current_token_text
            self.symbolTable.define(name,type,"argument")
            ###
            #varName
            self.advance()
            while self.current_token_text == ",":
                    self.eat([","])
                    ###
                    type = self.current_token_text
                    ###
                    #type
                    self.advance()
                    ###
                    name = self.current_token_text
                    self.symbolTable.define(name,type,"argument")
                    ###
                    #varName
                    self.advance()
        self.out_puts.append("</parameterList>")
        
    # subroutineBody: '{' varDec* statements '}'
    def compileSubroutineBody(self, type):
        self.out_puts.append("<subroutineBody>")
        ###
        if type == "constructor":
            self.vmWriter.writePush("constant", self.symbolTable.varCount("field"))
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        elif type == "method":
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)
        ###
        self.eat(["{"])
        # varDec*
        while self.current_token_text in ["var"]:
            self.compileVarDec()
        # statements
        self.compileStatements()
        self.eat(["}"])
        self.out_puts.append("</subroutineBody>")
    
    # varDec: 'var' type varName(',' type varName)* ';'
    def compileVarDec(self):
        self.out_puts.append("<varDec>")
        self.eat(["var"])
        ###
        type = self.current_token_text
        ###
        #type
        self.advance()
        ###
        name = self.current_token_text
        self.symbolTable.define(name,type,"local")
        ###
        #varName
        self.advance()
        if self.current_token_text == ",":
            while self.current_token_text != ";":
                self.eat([","])
                ###
                name = self.current_token_text
                self.symbolTable.define(name,type,"local")
                ###
                #varName
                self.advance()
        self.eat([";"])
        self.out_puts.append("</varDec>")

    # statements: statement*
    # statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
    def compileStatements(self):
        self.out_puts.append("<statements>")
        while self.current_token_text in ["let","if","while","do","return"]:
            if self.current_token_text == "let":
                self.compileLet()
            elif self.current_token_text == "if":
                self.compileIf()
            elif self.current_token_text == "while":
                self.compileWhile()
            elif self.current_token_text == "do":
                self.compileDo()
            elif self.current_token_text == "return":
                self.compileReturn()
        self.out_puts.append("</statements>")
    
    # letStatement: 'let' varName ('[' expression ']')? '=' expression';'
    def compileLet(self):
        self.out_puts.append("<letStatement>")
        self.eat("let")
        ###
        varName = self.current_token_text
        isArrayLet = False
        ###
        self.advance()
        if self.current_token_text == "[":
            self.eat("[")
            self.compileExpression()
            self.eat("]")
            ###
            isArrayLet = True
            segment = self.symbolTable.kindOf(varName)
            if segment == "field": segment = "this"
            self.vmWriter.writePush(segment, self.symbolTable.indexOf(varName))
            self.vmWriter.writeArithmetic("+")
            ###
        self.eat("=")
        self.compileExpression()
        self.eat(";")
        ###
        if isArrayLet:
            self.vmWriter.writePop("temp", 0)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePush("temp", 0)
            self.vmWriter.writePop("that", 0)
        else:
            segment = self.symbolTable.kindOf(varName)
            if segment == "field": segment = "this"
            self.vmWriter.writePop(segment, self.symbolTable.indexOf(varName))
        ###
        self.out_puts.append("</letStatement>")
    
    # ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compileIf(self):
        ###
        L1 = "IF_TRUE{}".format(self.ifLabelIndex)
        L2 = "IF_FALSE{}".format(self.ifLabelIndex)
        self.ifLabelIndex += 1
        ###
        self.out_puts.append("<ifStatement>")
        self.eat("if")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        ###
        self.vmWriter.writeArithmetic("~")
        self.vmWriter.writeIf(L1)
        ###
        self.eat("{")
        self.compileStatements()
        self.eat("}")
        ###
        self.vmWriter.writeGoto(L2)
        self.vmWriter.writeLabel(L1)
        ###
        if self.current_token_text == "else":
            self.eat("else")
            self.eat("{")
            self.compileStatements()
            self.eat("}")
        ###
        self.vmWriter.writeLabel(L2)
        ###
        self.out_puts.append("</ifStatement>")
        
    # whileStatement: 'while' '(' expression ')' '(' statements ')'
    def compileWhile(self):
        ###
        L1 = "WHILE_EXP{}".format(self.whileLabelIndex)
        L2 = "WHILE_END{}".format(self.whileLabelIndex)
        self.whileLabelIndex += 1
        ###
        self.out_puts.append("<whileStatement>")
        ###
        self.vmWriter.writeLabel(L1)
        ###
        self.eat("while")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        ###
        self.vmWriter.writeArithmetic("~")
        self.vmWriter.writeIf(L2)
        ###
        self.eat("{")
        self.compileStatements()
        self.eat("}")
        ###
        self.vmWriter.writeGoto(L1)
        self.vmWriter.writeLabel(L2)
        ###
        self.out_puts.append("</whileStatement>")
    
    # doStatement: 'do' subroutineCall';
    # subroutineCall: subroutineName '(' expressionList ')' | (className | varName '.' subroutineName "(' expressionList ')'
    def compileDo(self):
        self.out_puts.append("<doStatement>")
        self.eat("do")
        ###
        name = self.current_token_text
        ###
        self.advance()
        if self.current_token_text == ".":
            ###
            name += self.current_token_text
            ###
            self.eat(".")
            ###
            name += self.current_token_text
            ###
            self.advance()
        ###
        if "." in name:
            arr = name.split(".")
            type = self.symbolTable.typeOf(arr[0])
            #objcName
            if type:
                kind = self.symbolTable.kindOf(arr[0])
                if kind == "field": kind = "this"
                index = self.symbolTable.indexOf(arr[0])
                self.vmWriter.writePush(kind, index)
        else:
            self.vmWriter.writePush("pointer", 0)
        ###
        self.eat("(")
        nArgs = self.compileExpressionList()
        self.eat(")")
        self.eat(";")
        ###
        if "." in name:
            arr = name.split(".")
            type = self.symbolTable.typeOf(arr[0])
            #objcName
            if type:
                self.vmWriter.writeCall(type + "." +  arr[1], nArgs + 1)
            #className
            else:
                self.vmWriter.writeCall(name, nArgs)
        else:
            self.vmWriter.writeCall(self.className + "." +  name, nArgs + 1)
        self.vmWriter.writePop("temp", 0)
        ###
        self.out_puts.append("</doStatement>")
    
    # ReturnStatement: 'return' expression?';'
    def compileReturn(self):
        self.out_puts.append("<returnStatement>")
        self.eat("return")
        isOnlyReturn = True
        if self.current_token_text != ";":
            isOnlyReturn = False
            self.compileExpression()
        self.eat(";")
        ###
        if isOnlyReturn: self.vmWriter.writePush("constant", 0)
        self.vmWriter.writeReturn()
        ###
        self.out_puts.append("</returnStatement>")
    
    # expression: term (op term)*
    def compileExpression(self):
        self.out_puts.append("<expression>")
        self.compileTerm()
        while self.current_token_text in ["+","-","*","/","&amp;","|","&lt;","&gt;","="]:
            ###
            symbol = self.current_token_text
            ###
            self.eat(["+","-","*","/","&amp;","|","&lt;","&gt;","="])
            self.compileTerm()
            ###
            self.vmWriter.writeArithmetic(symbol)
            ###
        self.out_puts.append("</expression>")
    
    # term: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
    def compileTerm(self):
        self.out_puts.append("<term>")
        # '(' expression ')'
        if self.current_token_text == "(":
            self.eat("(")
            self.compileExpression()
            self.eat(")")
        #  unaryOp term
        elif self.current_token_text in ["-","~"]:
            symbol = self.current_token_text
            self.eat(["-","~"])
            self.compileTerm()
            ###
            if symbol == "-":
                self.vmWriter.writeArithmetic(symbol*2)
            else:
                self.vmWriter.writeArithmetic(symbol)
            ###
        # integerConstant
        elif "<integerConstant>" in self.current_token:
            self.vmWriter.writePush("constant",self.current_token_text)
            self.advance()
        # stringConstant
        elif "<stringConstant>" in self.current_token:
            str = self.current_token_text
            self.vmWriter.writePush("constant", len(str))
            self.vmWriter.writeCall("String.new", 1)
            for c in str:
                self.vmWriter.writePush("constant", ord(c))
                self.vmWriter.writeCall("String.appendChar", 2)
            self.advance()
        # keywordConstant
        elif "<keyword>" in self.current_token:
            if self.current_token_text in ["true","false","null","this"]:
                if self.current_token_text == "this":
                    self.vmWriter.writePush("pointer",0)
                elif self.current_token_text == "true":
                    self.vmWriter.writePush("constant",1)
                    self.vmWriter.writeArithmetic("--")
                else:
                    self.vmWriter.writePush("constant",0)
            self.advance()
        else:
            varName = self.current_token_text
            self.advance()
            # varName '[' expression ']'
            if self.current_token_text == "[":
                ###
                segment = self.symbolTable.kindOf(varName)
                if segment == "field": segment = "this"
                self.vmWriter.writePush(segment, self.symbolTable.indexOf(varName))
                ###
                self.eat("[")
                self.compileExpression()
                self.eat("]")
                ###
                self.vmWriter.writeArithmetic("+")
                self.vmWriter.writePop("pointer", 1)
                self.vmWriter.writePush("that", 0)
                ###
            # subroutineCall: subroutineName'('expressionList')' | (className | varName)'.'subroutineName'('expressionList')'
            elif self.current_token_text == "." or self.current_token_text == "(":
                if self.current_token_text == ".":
                    varName += self.current_token_text
                    self.eat(".")
                    varName += self.current_token_text
                    self.advance()
                ###
                if "." in varName:
                    arr = varName.split(".")
                    type = self.symbolTable.typeOf(arr[0])
                    #objcName
                    if type:
                        kind = self.symbolTable.kindOf(arr[0])
                        if kind == "field": kind = "this"
                        index = self.symbolTable.indexOf(arr[0])
                        self.vmWriter.writePush(kind, index)
                else:
                    self.vmWriter.writePush("pointer", 0)
                ###
                self.eat("(")
                nArgs = self.compileExpressionList()
                self.eat(")")
                ###
                if "." in varName:
                    arr = varName.split(".")
                    type = self.symbolTable.typeOf(arr[0])
                    #objcName
                    if type:
                        self.vmWriter.writeCall(type + "." +  arr[1], nArgs + 1)
                    #className
                    else:
                        self.vmWriter.writeCall(varName, nArgs)
                else:
                    self.vmWriter.writeCall(self.className + "." +  varName, nArgs + 1)
                ###
            #varName
            else:
                ###
                segment = self.symbolTable.kindOf(varName)
                if segment == "field": segment = "this"
                self.vmWriter.writePush(segment, self.symbolTable.indexOf(varName))
                ###
        self.out_puts.append("</term>")
    
    # expressionList: (expression (',' expression)*)?
    def compileExpressionList(self):
        n = 0
        self.out_puts.append("<expressionList>")
        if self.current_token_text != ")":
            self.compileExpression()
            n = 1
            while self.current_token_text == ",":
                n += 1
                self.eat(",")
                self.compileExpression()
        self.out_puts.append("</expressionList>")
        return n

    @property
    def current_token_text(self):
        text = re.findall(r'<[^>]*>(.*?)<\/[^>]*>',self.current_token)[0]
        return text[1:len(text)-1]
    
    @property
    def prettify_xml(self):
        parsed_xml = xml.dom.minidom.parseString("".join(self.out_puts))
        pretty_xml = parsed_xml.toprettyxml(indent='  ')
        if '<?xml' in pretty_xml:
            pretty_xml = pretty_xml.split('\n', 1)[1]  # 移除第一行
        return pretty_xml
    
    def outputXML(self):
        fileName = os.path.splitext(os.path.basename(self.file))[0]
        with open('{}.xml'.format(fileName), 'w') as f:
            f.write(self.prettify_xml)
            
    def outputVM(self):
        fileName = ""
        dirName = ""
        if os.path.isdir(self.file):
            fileName = os.path.basename(self.file)
            dirName = self.file
        else:
            fileName = os.path.splitext(os.path.basename(self.file))[0]
            dirName = os.path.dirname(self.file)
        fileName = os.path.splitext(os.path.basename(self.file))[0]
        with open(dirName + "/" + fileName + ".vm", 'w') as f:
            f.write(self.vmWriter.output())

if __name__ == "__main__":
    engine = CompilationEngine("Main.jack")
    # 测试打印
    # for token in engine.out_puts:
    #     print(token)
    # 测试XML输出
    engine.outputXML()
    # 测试XML输出
    engine.outputVM()
    
    print(engine.symbolTable.classTable)
    print(engine.symbolTable.subroutineTable)