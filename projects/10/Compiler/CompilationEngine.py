import re
import os
import xml.dom.minidom
from JackTokenizer import JackTokenizer


class CompilationEngine:
    def __init__(self, file):

        self.file = file
        self.out_puts = []
        self.tokenizer = JackTokenizer(file)
        self.current_token = self.tokenizer.next()
        self.compileClass()

    # 检验当前token和语法规则是否匹配
    def eat(self, tokens):
        if self.current_token_text in tokens:
            self.advance()
        else:
            print("ERROR: current_token_text {} tokens{}".format(
                self.current_token_text, tokens))

    # 添加到新的输出 并取出下一个 token
    def advance(self):
        if self.current_token:
            self.out_puts.append(self.current_token)
        self.current_token = self.tokenizer.next()

    # class: 'class' className '{' classVarDec* subroutineDec* '}'
    def compileClass(self):
        self.out_puts.append("<class>")
        self.eat(["class"])
        # className
        self.advance()
        self.eat(["{"])
        # classVarDec*
        while self.current_token_text in ["static", "field"]:
            self.compileClassVarDec()
        # subroutineDec*
        while self.current_token_text in ["constructor", "function", "method"]:
            self.compileSubroutineDec()
        self.eat(["}"])
        self.out_puts.append("</class>")

    # classVarDec: ('static'|'field') type varName (', ' varName)* ';'
    # type: 'int' | 'char' | 'boolean' | className
    def compileClassVarDec(self):
        self.out_puts.append("<classVarDec>")
        # ('static'|'field')
        self.eat(["static", "field"])
        # type
        self.advance()
        # varName
        self.advance()
        # (','varName)*
        if self.current_token_text == ",":
            while self.current_token_text != ";":
                self.eat([","])
                self.advance()
        self.eat([";"])
        self.out_puts.append("</classVarDec>")

    # subroutineDec: ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody
    def compileSubroutineDec(self):
        self.out_puts.append("<subroutineDec>")
        self.eat(["constructor", "function", "method"])
        self.advance()
        self.advance()
        self.eat(["("])
        self.compileParameterList()
        self.eat([")"])
        self.compileSubroutineBody()
        self.out_puts.append("</subroutineDec>")

    # parameterList: ((type varName) (',' type varName)*)?
    def compileParameterList(self):
        self.out_puts.append("<parameterList>")
        if self.current_token_text != ")":
            self.advance()
            self.advance()
            while self.current_token_text == ",":
                self.eat([","])
                self.advance()
                self.advance()
        self.out_puts.append("</parameterList>")

    # subroutineBody: '{' varDec* statements '}'
    def compileSubroutineBody(self):
        self.out_puts.append("<subroutineBody>")
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
        self.advance()
        self.advance()
        if self.current_token_text == ",":
            while self.current_token_text != ";":
                self.eat([","])
                self.advance()
        self.eat([";"])
        self.out_puts.append("</varDec>")

    # statements: statement*
    # statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
    def compileStatements(self):
        self.out_puts.append("<statements>")
        while self.current_token_text in ["let", "if", "while", "do", "return"]:
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
        self.advance()
        if self.current_token_text == "[":
            self.eat("[")
            self.compileExpression()
            self.eat("]")
        self.eat("=")
        self.compileExpression()
        self.eat(";")
        self.out_puts.append("</letStatement>")

    # ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compileIf(self):
        self.out_puts.append("<ifStatement>")
        self.eat("if")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.eat("}")
        if self.current_token_text == "else":
            self.eat("else")
            self.eat("{")
            self.compileStatements()
            self.eat("}")
        self.out_puts.append("</ifStatement>")

    # whileStatement: 'while' '(' expression ')' '(' statements ')'
    def compileWhile(self):
        self.out_puts.append("<whileStatement>")
        self.eat("while")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.eat("}")
        self.out_puts.append("</whileStatement>")

    # doStatement: 'do' subroutineCall';
    # subroutineCall: subroutine Name '(' expressionList ')' | (className | varName'.' subroutine Name "(' expressionList ')'
    def compileDo(self):
        self.out_puts.append("<doStatement>")
        self.eat("do")
        self.advance()
        if self.current_token_text == ".":
            self.eat(".")
            self.advance()
        self.eat("(")
        self.compileExpressionList()
        self.eat(")")
        self.eat(";")
        self.out_puts.append("</doStatement>")

    # ReturnStatement: 'return' expression?';'
    def compileReturn(self):
        self.out_puts.append("<returnStatement>")
        self.eat("return")
        if self.current_token_text != ";":
            self.compileExpression()
        self.eat(";")
        self.out_puts.append("</returnStatement>")

    # expression: term (op term)*
    def compileExpression(self):
        self.out_puts.append("<expression>")
        self.compileTerm()
        while self.current_token_text in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
            self.eat(["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="])
            self.compileTerm()
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
        elif self.current_token_text in ["-", "~"]:
            self.eat(["-", "~"])
            self.compileTerm()
        else:
            # integerConstant | stringConstant | keywordConstant | varName
            self.advance()
            # varName '[' expression ']'
            if self.current_token_text == "[":
                self.eat("[")
                self.compileExpression()
                self.eat("]")
            # subroutineCall
            elif self.current_token_text == "." or self.current_token_text == "(":
                if self.current_token_text == ".":
                    self.eat(".")
                    self.advance()
                self.eat("(")
                self.compileExpressionList()
                self.eat(")")
        self.out_puts.append("</term>")

    # expressionList: (expression (',' expression)*)?
    def compileExpressionList(self):
        self.out_puts.append("<expressionList>")
        if self.current_token_text != ")":
            self.compileExpression()
            while self.current_token_text == ",":
                self.eat(",")
                self.compileExpression()
        self.out_puts.append("</expressionList>")

    @property
    def current_token_text(self):
        text = re.findall(r'<[^>]*>(.*?)<\/[^>]*>', self.current_token)[0]
        text = text.strip()
        return text

    @property
    def prettify_xml(self):
        parsed_xml = xml.dom.minidom.parseString("".join(self.out_puts))
        pretty_xml = parsed_xml.toprettyxml(indent='  ')
        if '<?xml' in pretty_xml:
            pretty_xml = pretty_xml.split('\n', 1)[1]  # 移除第一行
        return pretty_xml

    def output(self):
        fileName = os.path.splitext(os.path.basename(self.file))[0]
        with open('{}.xml'.format(fileName), 'w') as f:
            f.write(self.prettify_xml)


if __name__ == "__main__":
    engine = CompilationEngine("../Square/SquareGame.jack")
    # 测试打印
    for token in engine.out_puts:
        print(token)
    # 测试输出
    engine.output()
