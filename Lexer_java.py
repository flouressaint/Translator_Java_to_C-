import Token
import re

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
    "||": "OR",
    "!": "NOT",
    "(": "LEFT_BRACKET",
    ")": "RIGHT_BRACKET",
    "[": "LEFT_SQUARE_BRACKET",
    "]": "RIGHT_SQUARE_BRACKET",
    "{": "LEFT_CURL_BRACKET",
    "}": "RIGHT_CURL_BRACKET",
    ".": "DOT",
    ";": "SEMICOLON",
    ",": "SEMI"
}


IGNORE = ["\n", " ", "\t", ":"]


class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}\t:{self.value}"


class Lexer:
    def __init__(self, source):
        self.state = None
        self.source = source
        self.pos = -1
        self.len = -1

    """
    Функция get_char смещает наш указатель (self.pos), потом
    возвращает символ из текста программы и, если наш указатель
    превысил длину строки то значит мы дошли до конца файла
    и ставим наш статус равный "EOF" (end of file)
    """
    def get_char(self, text):
        self.pos += 1
        if self.pos < self.len:
            return text[self.pos]
        else:
            self.state = "EOF"
            return ""

    def get_lexem(self, text):
        accum = ""  # накапливает символы из текста программы
        self.state = "START"  # начальный статус
        ch = self.get_char(text)

        """
        Разбираем текст программы до тех пор, пока наш статус не
        None или не конец файла "EOF"
        """
        while self.state is not None and self.state != "EOF":
            while ch in IGNORE:
                ch = self.get_char(text)

            """
            Если первым символом встретили не букву и не цифру, то проверяем находится ли
            символ (ch) в OPERATORS, если да, то накапливаем все не буквы и не цифры,
            которые идут следом и как только встретим что-то из OPERATORS, то возвращаем
            полученный результат
            
            ============================ Возможны ошибки ============================
            Надо проверить, что будет если наша последовательность не попадет в OPERATORS
            """
            if not ch.isalpha() and not ch.isnumeric():
                while not ch.isalnum():
                    accum += ch
                    if accum in OPERATORS:
                        return Token(accum, OPERATORS[accum])
                    ch = self.get_char(text)

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
                    self.state = "ID"
                    accum += ch
                    if accum in ACCESS_MODIFIERS:
                        return Token(accum, ACCESS_MODIFIERS[accum])
                    elif accum in KEY_WORDS:
                        return Token(accum, KEY_WORDS[accum])
                    elif accum in DATA_TYPES:
                        return Token(accum, DATA_TYPES[accum])
                    ch = self.get_char(text)
                self.pos -= 1
                return Token(accum, "ID")

            """
            Если первым символом встретили цифру, то переходим в состояние "NUM"
            и начинаем собирать следующие цифры.
            Если встретили точку, то продолжаем собирать число.
            Все выше сказанное делаем до тех пор, пока не встретим не цифру или не точку
            
            ============================ Возможны ошибки ============================
            Надо проверять
            """
            if ch.isnumeric():
                self.state = "NUM"
                while ch.isnumeric():
                    accum += ch
                    ch = self.get_char(text)
                    if ch == ".":
                        accum += ch
                        ch = self.get_char(text)
                # Если наше число заканчивается на точку, то выкидываем ошибку
                if accum[len(accum) - 1] == ".":
                    raise SyntaxError("Invalid real number, in position {}".format(self.pos))

                self.pos -= 1
                return Token(accum, "NUM")

    """
    Начало начало - метод parse. Он открывает файл с исходным кодом на Java
    считывает оттуда все строки и пошло поехало...
    """
    def parse(self):
        with open(self.source, "r") as file:
            text = file.read()

        if len(text) == 0:
            return
        self.len = len(text)
        while self.state != "EOF":
            c = self.get_lexem(text)
            if c is not None:
                print(c)  # Здесь выводятся все наши токены потом можно как-то собрать


class SyntaxError(BaseException):
    pass
