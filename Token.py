ACCESSMODIFIERS = {
    "PUBLIC": "public",
    "PRIVATE": "private",
    "PROTECTED": "protected",
}

KEYWORDS = {
    "ABSTRACT": "abstract",
    "BREAK": "break",
    "CASE": "case",
    "CATCH": "catch",
    "CLASS": "class",
    "CONTINUE": "continue",
    "DEFAULT": "default",
    "DO": "do",
    "ELSE": "else",
    "ENUM": "enum",
    "EXTENDS": "extends",
    "FOR": "for",
    "IF": "if",
    "IMPLEMENTS": "implements",
    "IMPORT": "import",
    "INSTANCEOF": "instanceof",
    "INTERFACE": "interface",
    "NEW": "new",
    "PACKAGE": "package",
    "RETURN": "return",
    "STATIC": "static",
    "SUPER": "super",
    "SWITCH": "switch",
    "SYNCHRONIZED": "synchronized",
    "THIS": "this",
    "THROW": "throw",
    "THROWS": "throws",
    "TRANSIENT": "transient",
    "TRY": "try",
    "WHILE": "while"
}

DATATYPES = {
    "BYTE": "byte",
    "SHORT": "short",
    "INT": "int",
    "LONG": "long",
    "FLOAT": "float",
    "DOUBLE": "double",
    "BOOLEAN": "boolean",
    "CHAR": "char",
    "STRING": "string",
    "VOID": "void"
}

OPERATORS = {
    "ASSIGN": "=",
    "EQUAL": "==",
    "MOREOREQUAL": ">=",
    "LESSOREQUAL": "<=",
    "PLUS": "+",
    "MINUS": "-",
    "MUL": "*",
    "DIV": "/",
    "MOD": "%",
    "PLUSPLUS": "++",
    "MINMIN": "--",
    "SHORTPLUS": "+=",
    "SHORTMINUS": "-=",
    "SHORTMUL": "*=",
    "SHORTDIV": "/=",
    "SHORTMOD": "%=",
    "SHORTAND": "&=",
    "SHORTOR": "|=",
    "SHORTPOW": "^=",
    "SHORTBITESHIFTRIGHT": ">>=",
    "SHORTBITESHIFTLEFT": "<<=",
    "NOTEQUAL": "!=",
    "AND": "&&",
    "OR": "||",
    "NOT": "!",
    "LEFTBRACKET": "(",
    "RIGHTBRACKET": ")",
    "LEFTSQUAREBRACKET": "[",
    "RIGHTSQUAREBRACKET": "]",
    "DOUBLEDOT": "..",
    "DOT": ".",
    "POW": "^",
    "LESS": "<",
    "MORE": ">"
}


class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}\t{self.value}"
