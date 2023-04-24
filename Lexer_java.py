class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}\t{self.value}"

class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.token = Token(None, None)

    def _next_token(self):
        if self.pos >= len(self.source):
            return Token('eof', None)
        ch = self.source[self.pos]
        self.pos += 1
        if ch.isnumeric(): return Token('num', int(ch))
        if ch.isalpha(): return Token('id', ch)
        return Token(ch, None)

    def next_token(self):
        self.token = self._next_token()
        return self.token
    
import re

# Define regular expressions for each token
regex_patterns = {
    'VAR': r'var',
    'PROGRAM': r'program',
    'BEGIN': r'begin',
    'END': r'end',
    'INTEGER': r'integer',
    'REAL': r'real',
    'BOOLEAN': r'boolean',
    'CHAR': r'char',
    'ARRAY': r'array',
    'OF': r'of',
    'IF': r'if',
    'THEN': r'then',
    'ELSE': r'else',
    'WHILE': r'while',
    'DO': r'do',
    'REPEAT': r'repeat',
    'UNTIL': r'until',
    'FOR': r'for',
    'TO': r'to',
    'DOWNTO': r'downto',
    'FUNCTION': r'function',
    'PROCEDURE': r'procedure',
    'NOT': r'not',
    'IDENTIFIER': r'[a-zA-Z][a-zA-Z0-9_]*',
    'NUMBER': r'[0-9]+',
    'PLUS': r'\+',
    'MINUS': r'\-',
    'MULTIPLY': r'\*',
    'DIVIDE': r'\/',
    'ASSIGN': r':=',
    'SEMICOLON': r';',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'DOT': r'\.',
    'COMMA': r',',
    'COLON': r':',

}

# Combine all the regex patterns into one regular expression
token_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in regex_patterns.items()))


def tokenize(code):
    tokens = []
    line_number = 1
    for match in token_regex.finditer(code):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        if token_type == 'IDENTIFIER':
            if not re.match(r'^[a-zA-Z]+$', token_value):
                raise ValueError(f'SyntaxError: Invalid variable name "{token_value}" on line {line_number}')
        elif token_type == 'NUMBER':
            try:
                int_value = int(token_value)
            except ValueError:
                raise ValueError(f'SyntaxError: Invalid integer "{token_value}" on line {line_number}')
            if not -32768 <= int_value <= 32767:
                raise ValueError(f'ValueError: Integer overflow "{token_value}" on line {line_number}')
        elif token_type == 'SEMICOLON':
            line_number += 1
        tokens.append((token_type, token_value))
    return tokens


def main():
    with open('file.pas', 'r') as file:
        code = file.read()

    try:
        tokens = tokenize(code)
        for token in tokens:
            print(token)
    except ValueError as e:
        print('Error:', str(e))
        return

    print('Parsed successfully!')


if __name__ == '__main__':
    main()