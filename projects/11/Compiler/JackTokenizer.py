import re
import os
import sys
os.chdir(sys.path[0])


class JackTokenizer:
    def __init__(self, file):

        self.file = file
        self.index = 0
        self.xml_tokens = []

        # Jack 语言的关键字
        keywords = ['class', 'constructor', 'function', 'method', 'field', 'static',
                    'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
                    'this', 'let', 'do', 'if', 'else', 'while', 'return']

        # Jack 语言的符号
        symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
                   '/', '&', '|', '<', '>', '=', '~']

        symbols_map = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}

        # 读取 Jack 代码
        with open(file, "r") as f:
            jack_code = f.read()

        # 去除注释
        jack_code = re.sub(r'//.*?\n', '', jack_code)  # 去除行注释
        jack_code = re.sub(r'/\*.*?\*/', '', jack_code,
                           flags=re.DOTALL)  # 去除块注释

        # 分词
        tokens = []
        current_token = ''
        is_string = False
        for char in jack_code:
            if char == '"':
                if current_token:
                    current_token += char
                    tokens.append(current_token)
                    current_token = ''
                    is_string = False
                else:
                    current_token += char
                    is_string = True
            else:
                if char in symbols and not is_string:
                    if current_token:
                        tokens.append(current_token)
                    tokens.append(char)
                    current_token = ''
                # 检查一个字符是否为空白字符，包括空格、制表符、换行符等
                elif char.isspace() and not is_string:
                    if current_token:
                        tokens.append(current_token)
                        current_token = ''
                else:
                    current_token += char

        if current_token:
            tokens.append(current_token)

        # 标识符和关键字的分类
        for i, token in enumerate(tokens):
            if token in keywords:
                tokens[i] = "<keyword> {} </keyword>".format(token)
            elif token in symbols:
                if token in symbols_map:
                    token = symbols_map[token]
                tokens[i] = "<symbol> {} </symbol>".format(token)
            elif token.isdigit():
                tokens[i] = "<integerConstant> {} </integerConstant>".format(
                    int(token))
            elif self.isstring(token):
                tokens[i] = "<stringConstant> {} </stringConstant>".format(
                    re.findall(r"^\"(.*?)\"$", token)[0])
            else:
                tokens[i] = "<identifier> {} </identifier>".format(token)

        self.xml_tokens = tokens

    def isstring(self, token):
        return re.match(r"^\".*\"$", token)

    def next(self):
        if self.index < len(self.xml_tokens):
            token = self.xml_tokens[self.index]
            self.index += 1
            return token
        return None

    def output(self):
        fileName = os.path.splitext(os.path.basename(self.file))[0]
        with open('{}T.xml'.format(fileName), 'w') as f:
            xml = ''
            for token in self.xml_tokens:
                xml += token + "\n"
            f.write(xml)


if __name__ == "__main__":
    tokenizer = JackTokenizer("../ArrayTest/Main.jack")
    # 测试输出
    tokenizer.xml_tokens.insert(0, "<tokens>")
    tokenizer.xml_tokens.append("</tokens>")
    tokenizer.output()
