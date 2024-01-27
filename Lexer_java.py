class help:
    ACCESS_MODIFIERS = {
        "public": "PUBLIC",
        "private": "PRIVATE",
        "protected": "PROTECTED",
    }

    KEY_WORDS = {
        "class": "CLASS",
        "else": "ELSE",
        "for": "FOR",
        "if": "IF",
        "new": "NEW",
        "package": "PACKAGE",
        "return": "RETURN",
        "static": "STATIC",
        "this": "THIS",
        "while": "WHILE",
        "System.out.print": "SYSTEM.OUT.PRINT",
        "System.out.println": "SYSTEM.OUT.PRINTLN",
        "switch": "SWITCH",
        "case": "CASE",
        "default": "DEFAULT"
    }

    DATA_TYPES = {
        "byte": "BYTE",
        "short": "SHORT",
        "int": "INT",
        "long": "LONG",
        "float": "FLOAT",
        "double": "DOUBLE",
        "boolean": "boolean",
        "char": "CHAR",
        "string": "STRING",
        "void": "VOID",
    }

    OPERATORS = {
        "=": "ASSIGN",
        "==": "IS_EQUAL",
        "!=": "INEQUALITY",
        "<": "LESS",
        ">": "MORE",
        ">=": "GRATER_THAN_OR_EQUAL",
        "<=": "LESS_THAN_OR_EQUAL",
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLE",
        "/": "DIVIDE",
        "%": "MOD",
        "++": "INCREMENT",
        "--": "DECREMENT",
        "+=": "EDITION",
        "-=": "SUBTRACTION",
        "*=": "MULTIPLICATION",
        "/=": "DIVISION",
        "%=": "MODULUS",
        "&&": "AND",
        "&": "SHORT_AND",
        "||": "OR",
        "|": "SHORT_OR",
        "!": "NOT",
        ":": "DOUBLE_DOT",
    }

    SPEC = {
        "(": "LEFT_BRACKET",
        ")": "RIGHT_BRACKET",
        "[": "LEFT_SQUARE_BRACKET",
        "]": "RIGHT_SQUARE_BRACKET",
        "{": "LEFT_CURL_BRACKET",
        "}": "RIGHT_CURL_BRACKET",
        ".": "DOT",
        ";": "SEMICOLON",
        ",": "COMMA",
        "//": "DOUBLE_SLASH"
    }

    IGNORE = ["\n", " ", "\t"]


class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}\t:{self.value}"


class Lexer:
    text = ""
    flow_lexem = []
    START, COMMENT, EOF, STRING, CHAR, OPERATOR, ID, INT, DOUBLE, BOOLEAN = range(10)
    STATES = {
        START: "START",
        COMMENT: "COMMENT",
        EOF: "EOF",
        STRING: "string",
        CHAR: "char",
        OPERATOR: "OPERATOR",
        ID: "ID",
        INT: "int",
        DOUBLE: "double",
        BOOLEAN: "boolean"
    }

    def __init__(self, source):
        if self.text == "":
            with open(source, "r") as file:
                self.text = file.read()
        self.state = None
        self.source = source
        self.pos = -1
        self.position = -1
        self.lineno = 0
        self.len = len(self.text)

    """
    Функция get_char смещает наш указатель (self.pos), потом
    возвращает символ из текста программы и, если наш указатель
    превысил длину строки то значит мы дошли до конца файла
    и ставим наш статус равный "EOF" (end of file)
    """
    def get_char(self):
        self.pos += 1
        self.position += 1
        if self.pos < self.len:
            return self.text[self.pos]
        else:
            self.state = Lexer.START
            return ""

    '''
        Возвращает 
    '''
    def get_next_token(self):
        # накапливает символы из текста программы
        accum = ""
        # начальный статус
        self.state = Lexer.START
        ch = self.get_char()

        """
        Разбираем текст программы до тех пор, пока наш статус не
        None или не конец файла "EOF"
        """
        while self.state is not None and self.state != Lexer.EOF:
            while ch in help.IGNORE:
                if ch == "\n":
                    self.lineno += 1
                    self.position = -1
                ch = self.get_char()

            """
            Для определения string
            """
            if ch == '"':
                self.state = Lexer.STRING
                ch = self.get_char()
                # Здесь нужно идти, пока состояние STRING, тогда получится через состояния
                while self.state == Lexer.STRING:
                    accum += ch
                    ch = self.get_char()
                    if ch == '"':
                        self.state = None
                return Token(accum, help.DATA_TYPES[Lexer.STATES[Lexer.STRING]])
            
            """
            Для определения char
            """
            if ch == "'":
                self.state = Lexer.CHAR
                ch = self.get_char()
                accum += ch
                ch = self.get_char()
                if ch != "'":
                    raise SyntaxError.SyntaxError("char", self.lineno, self.position)
                else:
                    return Token(accum, help.DATA_TYPES[Lexer.STATES[Lexer.CHAR]])

            if ch in help.SPEC:
                accum += ch
                return Token(accum, help.SPEC[ch])
            """
            Если первым символом встретили не букву и не цифру, то проверяем находится ли
            символ (ch) в OPERATORS, если да, то накапливаем все не буквы и не цифры,
            которые идут следом и как только встретим что-то из OPERATORS, то возвращаем
            полученный результат
            
            ============================ Возможны ошибки ============================
            Надо проверить, что будет если наша последовательность не попадет в OPERATORS
            """
            if ch in help.OPERATORS:
                self.state = Lexer.OPERATOR
                while self.state is not None:
                    accum += ch
                    ch = self.get_char()
                    if accum == "//":
                        while ch != "\n":
                            ch = self.get_char()
                    if ch == ";" or ch not in help.OPERATORS:
                        self.state = None
                self.pos -= 1
                if accum == "//":
                    accum = ""
                    self.state = Lexer.COMMENT
                elif accum in help.OPERATORS:
                    return Token(accum, help.OPERATORS[accum])
                else:
                    raise SyntaxError.SyntaxError("operator", self.lineno, self.position)

            """
            Если первым символом встретили букву, то переходим в состояние "ID" и начинаем собирать
            следующие буквы и/или цифры до тех пор, пока собранная последовательность
            не попадет в ACCESS_MODIFIERS, KEY_WORDS или DATA_TYPES. Если же не одну из
            категорий не попало, то значит это ID
            
            ============================ Возможны ошибки ============================
            Если в других методах не можете найти ошибку, то быть может она тут
            """
            if ch.isalpha():
                while ch.isalnum():
                    self.state = Lexer.ID
                    accum += ch

                    if accum == "System.out.print":
                        ch = self.get_char()
                        if ch == "l":
                            accum += ch
                            ch = self.get_char()
                            accum += ch
                            return Token(accum, help.KEY_WORDS[accum])
                        else:
                            self.pos -= 1
                            return Token(accum, help.KEY_WORDS[accum])

                    if accum in help.ACCESS_MODIFIERS:
                        return Token(accum, help.ACCESS_MODIFIERS[accum])
                    elif accum in help.KEY_WORDS:
                        return Token(accum, help.KEY_WORDS[accum])
                    elif accum in help.DATA_TYPES:
                        return Token(accum, help.DATA_TYPES[accum])
                    ch = self.get_char()
                    if accum in {"System", "System.out"} and ch == ".":
                        accum += ch
                        ch = self.get_char()
                
                self.pos -= 1
                if accum == "false" or accum == "true":
                    return Token(accum, help.DATA_TYPES[Lexer.STATES[Lexer.BOOLEAN]])
                else:
                    return Token(accum, Lexer.STATES[Lexer.ID])
            
            """
            Если первым символом встретили цифру, то переходим в состояние "NUM"
            и начинаем собирать следующие цифры.
            Если встретили точку, то продолжаем собирать число.
            Все выше сказанное делаем до тех пор, пока не встретим не цифру или не точку
            
            ============================ Возможны ошибки ============================
            Надо проверять
            """
            if ch.isnumeric():
                self.state = Lexer.INT
                while self.state is not None:
                    accum += ch
                    ch = self.get_char()
                    if ch == ".":
                        if self.state == Lexer.DOUBLE:
                            raise SyntaxError.SyntaxError("double", self.lineno, self.position)
                        self.state = Lexer.DOUBLE
                        accum += ch
                        ch = self.get_char()

                    if ch == ";" or ch in help.IGNORE:
                        self.state = None
                    # elif self.state == "DOUBLE" and ch == ".":
                    #     raise SyntaxError("Invalid data type: double {}".format(self.pos))
                    elif ch in help.SPEC:
                        self.state = None
                    elif ch in help.OPERATORS:
                        self.state = None
                    elif not ch.isnumeric():
                        if self.state == Lexer.DOUBLE:
                            raise SyntaxError.SyntaxError("double", self.lineno, self.position)
                        else:
                            raise SyntaxError.SyntaxError("integer", self.lineno, self.position)

                # Если наше число заканчивается на точку, то выкидываем ошибку
                if accum[len(accum) - 1] == ".":
                    raise SyntaxError.SyntaxError("real number", self.lineno, self.position)

                self.pos -= 1
                if "." in accum:
                    return Token(accum, help.DATA_TYPES[Lexer.STATES[Lexer.DOUBLE]])
                else:
                    return Token(accum, help.DATA_TYPES[Lexer.STATES[Lexer.INT]])

            if self.state == Lexer.START:
                self.state = Lexer.EOF
                return Token("EOF", Lexer.STATES[Lexer.EOF])

    """
    Начало начало - метод parse. Он открывает файл с исходным кодом на Java
    считывает оттуда все строки и пошло поехало...
    """
    def parse(self):
        if len(self.text) == 0:
            return

        self.len = len(self.text)
        if self.state == Lexer.EOF:
            return
        return self.get_next_token()


class SyntaxError(BaseException):
    @staticmethod
    def SyntaxError(text, line, pos):
        return f"Syntax error: {text} in line {line} position {pos}"
