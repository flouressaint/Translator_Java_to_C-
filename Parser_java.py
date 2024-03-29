import sys
import operator

from Lexer_java import Lexer, Token, help
from SymbolTable import SymbolTable
from CodeGenerator import CodeGenerator
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class Node:
    def __init__(self, children):
        self.children = children

    def __get_class_name(self):
        c = str(self.__class__)
        pos_1 = c.find('.') + 1
        pos_2 = c.find("'", pos_1)
        return f"{c[pos_1:pos_2]}"

    def __repr__(self, level=0):
        # словарь атрибут : значение
        # если атрибут один и тип его значения - это список,
        # то это узел некоторой последовательности (подпрограмма, либо список)
        attrs = self.__dict__
        
        if len(attrs) == 1 and isinstance(list(attrs.values())[0], list):
            is_sequence = True
        else:
            is_sequence = False
        res = f"{self.__get_class_name()}\n"
        if is_sequence:
            elements = list(attrs.values())[0]
            for el in elements:
                res += '|   ' * level
                res += "|+-"
                res += el.__repr__()
        else:
            for attr_name in attrs:
                res += '|   ' * level
                res += "|+-"
                if isinstance(attrs[attr_name], Token):
                    res += f"{attr_name}: {attrs[attr_name]}\n"
                else:
                    res += f"{attr_name}: {attrs[attr_name].__repr__()}"
        return res


class NodeProgram(Node):
    headerProgram = ""

    def setHeader(self, header):
        self.headerProgram = header

    def getGeneratedText(self):
        s = ""
        for item in self.children:
            s += item.getGeneratedText() + "\n"
        return s


class NodeBlock(NodeProgram):
    pass


class NodeSystemOutPrint(Node):
    def __init__(self, header, expression):
        self.header = header
        self.expression = expression
    
    def getGeneratedText(self):
        return self.header + "(" + self.expression.getGeneratedText() + ");\n"


class NodeDeclaration(Node):
    def __init__(self, _type, _id):
        self.type = _type
        self.id = _id

    def getGeneratedText(self):
        return self.type + " " + self.id


class NodeAssigning(Node):
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side

    def getGeneratedText(self):
        return self.left_side.getGeneratedText() + " = " + self.right_side.getGeneratedText() + ";"


class NodeMethod(Node):
    def __init__(self, access_mod, ret_type, _id, formal_params, block):
        self.access_mod = access_mod
        self.ret_type = ret_type
        self.id = _id
        self.formal_params = formal_params
        self.block = block

    def getGeneratedText(self):
        return self.access_mod.lower() + " " + \
               self.ret_type.lower() + " " + \
               self.id + "(" + self.formal_params.getGeneratedText() + ") " + \
               "\n{\n" + self.block.getGeneratedText() + "}"


class NodeSequence(Node):
    def __init__(self, members):
        self.members = members


class NodeParams(Node):
    def __init__(self, params):
        self.params = params


class NodeFormalParams(NodeParams):
    def getGeneratedText(self):
        s = ""
        for item in self.params:
            s += item.getGeneratedText() + ", "
        return s[:-2]


class NodeActualParams(NodeParams):
    def getGeneratedText(self):
        s = ""
        for item in self.params:
            s += item.getGeneratedText() + ", "


class NodeElseBlock(NodeBlock):
    pass


class NodeIfConstruction(Node):
    def __init__(self, condition, block, else_block=None):
        self.condition = condition
        self.block = block
        self.else_block = else_block

    def getGeneratedText(self):
        if self.else_block is None:
            return "if (" + self.condition.getGeneratedText() + ") " + \
                   " {\n" + self.block.getGeneratedText() + "}\n"
        else:
            return "if (" + self.condition.getGeneratedText() + ") " + \
                   " {\n" + self.block.getGeneratedText() + "}\n" + \
                   "else {\n" + self.else_block.getGeneratedText() + "}\n"


class NodeWhileConstruction(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def getGeneratedText(self):
        return "while (" + self.condition.getGeneratedText() + ") " + \
               "{\n" + self.block.getGeneratedText() + "}"


class NodeSwitchConstruction(Node):
    def __init__(self, tok, cases: list, blocks: list):
        self.tok = tok
        self.cases = cases
        self.blocks = blocks
    
    def getGeneratedText(self):
        s = "switch (" + self.tok + ") {\n"
        for i in range(len(self.cases)):
            s += "case " + self.cases[i].name + ":\n"
            if self.blocks[i] != "":
                s += self.blocks[i].getGeneratedText()
            s += "break;\n"
        s += "default:\n"
        if self.blocks[len(self.blocks) - 1] != "":
            s += self.blocks[len(self.blocks) - 1].getGeneratedText()
        s += "break;\n" + "}\n"
        return s
            

class NodeForConstruction(Node):
    def __init__(self, variable_declarator, expression, increment, block):
        self.var_declr = variable_declarator
        self.expr = expression
        self.incr = increment
        self.block = block

    def getGeneratedText(self):
        return "for (" + self.var_declr.getGeneratedText() + \
               self.expr.getGeneratedText() + ";" + \
               self.incr.getGeneratedText() + ") {\n" + \
               self.block.getGeneratedText() + "}"


class NodeReturnStatement(Node):
    def __init__(self, expression):
        self.expression = expression

    def getGeneratedText(self):
        return "return " + self.expression.getGeneratedText() + ";"


class NodeLiteral(Node):
    def __init__(self, value, _type=None):
        self.type = _type
        self.value = value

    def getGeneratedText(self):
        if self.type is None:
            return self.value.getGeneratedText()
        return self.value


class NodeStringLiteral(NodeLiteral):
    def getGeneratedText(self):
        return '"' + self.value + '"'


class NodeIntLiteral(NodeLiteral):
    pass


class NodeFloatLiteral(NodeLiteral):
    pass


class NodeBooleanLiteral(NodeLiteral):
    pass


class NodeVar(Node):
    def __init__(self, _id, _type):
        self.id = _id
        self.type = _type

    def getGeneratedText(self):
        return self.id + " " + self.type


class NodeAtomType(Node):
    def __init__(self, _id):
        self.id = _id

    def getGeneratedText(self):
        return self.id


class NodeComplexType(Node):
    def __init__(self, _id, size):
        self.id = _id
        self.size = size


class NodeFunctionCall(Node):
    def __init__(self, _id, actual_params):
        self.id = _id
        self.actual_params = actual_params


class NodeIndexAccess(Node):
    def __init__(self, var, index):
        self.var = var
        self.index = index


class NodeUnaryOperator(Node):
    def __init__(self, operand):
        self.operand = operand

    def getGeneratedText(self):
        return self.operand.getGeneratedText()


class NodeIncrement(Node):
    def __init__(self, _id):
        self.id = _id

    def getGeneratedText(self):
        return self.id + "++"


class NodeUnaryMinus(NodeUnaryOperator):
    def getGeneratedText(self):
        return "-" + self.operand.getGeneratedText()


class NodeNot(NodeUnaryOperator):
    def getGeneratedText(self):
        return "!" + self.operand.getGeneratedText()


class NodeBinaryOperator(Node):
    ops = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "%": operator.mod,
        "==": operator.eq,
        "!": operator.neg,
        "&&": operator.and_,
        "||": operator.or_,
        "<": operator.ge,
        ">": operator.gt
    }

    def __init__(self, left, right, operator=""):
        self.left = left
        self.right = right
        self.operator = operator

    def getGeneratedText(self):
        #if isinstance(self.left, NodeLiteral) and isinstance(self.right, NodeLiteral):
        #    if self.left.type == "int":
        #        return str(self.ops[self.operator](int(self.left.value), int(self.right.value)))
        #    elif self.left.type == "double":
        #        return str(self.ops[self.operator](float(self.left.value), float(self.right.value)))
        #else:
        return "(" + self.left.getGeneratedText() + " " + \
                self.operator + " " + self.right.getGeneratedText() + ")"


class NodeL(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "<"


class NodeG(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = ">"


class NodeLE(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "<="


class NodeGE(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = ">="


class NodeEQ(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "=="


class NodeNEQ(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "!="


class NodeOr(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "||"


class NodeAnd(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "&&"


class NodePlus(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "+"


class NodeMinus(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "-"


class NodeDivision(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "/"


class NodeMultiply(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "*"


class NodeIDivision(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "//"


class NodeMod(NodeBinaryOperator):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.operator = "%"


class Parser:
    ops = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "%": operator.mod,
        "==": operator.eq,
        "!": operator.neg,
        "&&": operator.and_,
        "||": operator.or_,
        "<": operator.ge,
        ">": operator.gt
    }

    typeNode = {
        "+": NodePlus,
        "-": NodeMinus,
        "*": NodeMultiply,
        "/": NodeDivision,
        "%": NodeMod,
        "==": NodeEQ,
        "!": NodeNot,
        "&&": NodeAnd,
        "||": NodeOr,
        "<": NodeL,
        ">": NodeG,
        "int": NodeIntLiteral,
        "double": NodeFloatLiteral,
        "string": NodeStringLiteral
    }

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = self.lexer.get_next_token()
        self.symbolTable = list()
        self.symbolTable.append(SymbolTable())

    def next_token(self):
        self.token = self.lexer.get_next_token()

    def error(self, msg):
        print(f'Ошибка синтаксического анализа: {msg}')
        sys.exit(1)

    def operand(self, _type) -> Node:
        first_token = self.token

        # Определяем тип операнда
        if self.token.value.lower() == "int":
            # Проверка на совпадение типов
            if _type != "boolean" and self.token.value.lower() != _type:
                self.error(SemanticErrors.TypeMismatch(self.lexer.lineno, self.lexer.position))
            self.next_token()
            return NodeIntLiteral(first_token.name, first_token.value.lower())
        elif self.token.value.lower() == "double":
            # Проверка на совпадение типов
            if _type != "boolean" and self.token.value.lower() != _type:
                self.error(SemanticErrors.TypeMismatch(self.lexer.lineno, self.lexer.position))
            self.next_token()
            return NodeFloatLiteral(first_token.name, first_token.value.lower())
        elif self.token.value.lower() == "string":
            self.next_token()
            return NodeStringLiteral(first_token.name, first_token.value.lower())
        # Если в качестве операнда выступает ID, то это может быть:
        # переменная, функция или массив.
        elif self.token.value == "ID":
            # Проверяем есть переменная в таблице символов, т.е. объявлена ли она
            f = False
            for table in self.symbolTable:
                if self.token.name in table.table:
                    f = True
            if not f:
                self.error(SemanticErrors.UnknowingIdentifier(self.token.name, self.lexer.lineno, self.lexer.position, "variable"))
            # Берем следующий токен
            self.next_token()
            # Если следующий токен это (, то значит операндом является функция
            if self.token.name == "(":
                pass
            # Если следующий токен это [, то значит операндом является массив
            elif self.token.name == "[":
                pass
            # Если не встретили ( и [, значит операндом является переменная
            else:
                if first_token.value == "ID":
                    return NodeAtomType(first_token.name)
                else:
                    return NodeVar(first_token.name, first_token.value.lower())
        # Если операндом является (, то значит мы встретили скобку в выражении
        # и должны продолжить разбор выражения, но уже в скобках.
        elif self.token.name == "(":
            self.next_token()
            expression = self.expression(_type)
            self.next_token()
            return expression

    # Этот метод определяет, есть ли у операнда унарный минус или нет.
    # А также начинает сам разбор операнда.
    def factor(self, _type) -> Node:
        if self.token.name == "-":
            self.next_token()
            return NodeUnaryMinus(self.operand(_type))
        elif self.token.name == "!":
            self.next_token()
            return NodeNot(self.operand(_type))
        else:
            return self.operand(_type)

    # Этот метод обрабатывает арифметическое выражение.
    # А именно выражение с операциями "*", "/", "<", ">", "==", "&&".
    def term(self, _type) -> Node:
        left = self.factor(_type)
        op = self.token.name

        while op in {"*", "/", "<", ">", "==", "&&"}:
            self.next_token()
            right = self.factor(_type)
            if isinstance(left, NodeLiteral) and isinstance(right, NodeLiteral):
                if _type == "int":
                    if op == "&&":
                        self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))
                    left = self.typeNode[_type](str(self.ops[op](int(left.value), int(right.value))), _type)
                elif _type == "double":
                    if op == "&&":
                        self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))
                    left = self.typeNode[_type](str(self.ops[op](float(left.value), float(right.value))), _type)
                elif _type == "boolean":
                    left = self.typeNode[op](left, right)
                else:
                    self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))
            else:
                left = self.typeNode[op](left, right)
            op = self.token.name
        return left

    # Этот метод обрабатывает арифметические выражения.
    # А именно выражения с операциями "+", "-", "||".
    def expression(self, _type) -> Node:
        left = self.term(_type)
        op = self.token.name

        while op in {"+", "-", "||"}:
            self.next_token()
            right = self.term(_type)
            if isinstance(left, NodeLiteral) and isinstance(right, NodeLiteral):
                if _type == "int":
                    if op != "||":
                        left = self.typeNode[_type](str(self.ops[op](int(left.value), int(right.value))), _type)
                    else:
                        self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))
                elif _type == "double":
                    if op != "||":
                        left = self.typeNode[_type](str(self.ops[op](float(left.value), float(right.value))), _type)
                    else:
                        self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))
                elif _type == "string":
                    if op == "+":
                        left = self.typeNode[_type](str(self.ops[op](left.value, right.value)), _type)
                    else:
                        self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))
                elif _type == "boolean":
                    left = self.typeNode[op](left, right)
                else:
                    self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))
            else:
                left = self.typeNode[op](left, right)
            op = self.token.name
        return left

    # Этот метод обрабатывает пары токенов вида: <type> <id>
    # или вида: <type> <id> = <right_side>
    def declaration(self) -> Node:
        # Сохраняем тип переменной или массива
        data_type = self.token.name
        self.next_token()
        if self.token.value == "ID":
            # Проверяем объявлена ли уже переменная.
            # Если объявлена, то выкидываем ошибку.
            #if self.symbolTable[len(self.symbolTable) - 1].isExist(self.token.name)
                #self.error(SemanticErrors.AlreadyDeclared())
            f = False
            for table in self.symbolTable:
                if self.token.name in table.table:
                    f = True
            if f:
                self.error(SemanticErrors.AlreadyDeclared(self.lexer.lineno, self.lexer.position))
            # Сохраняем id переменной
            _id = self.token.name
            self.next_token()
            # Проверяем на наличие знака =
            if self.token.name == "=":
                self.next_token()
                if self.token.value.lower() in help.DATA_TYPES or self.token.value == "ID":
                    # Добавляем переменную в таблицу символов
                    self.symbolTable[len(self.symbolTable) - 1].table[_id] = data_type

                    left_side = NodeDeclaration(data_type, _id)
                    right_side = NodeIntLiteral(self.expression(data_type))
                    if left_side.type != right_side.value.type:
                        self.error(SyntaxErrors.DeclarationError(self.lexer.lineno, self.lexer.position))


                    return NodeAssigning(left_side, right_side)
            # Добавляем переменную в таблицу символов
            self.symbolTable[len(self.symbolTable) - 1].table[_id] = data_type
            return NodeDeclaration(data_type, _id)
        # Обрабатываем объявление массивов.
        elif self.token.name == "[":
            self.next_token()
            if self.token.name != "]":
                self.error(SyntaxErrors.MissingSpecSymbol("]", self.lexer.lineno, self.lexer.position))
            self.next_token()
            if self.token.value != "ID":
                self.error(SyntaxErrors.MissingID(self.lexer.lineno, self.lexer.position))
            _id = self.token.name
            self.next_token()
        else:
            self.error(SyntaxErrors.DeclarationError(self.lexer.lineno, self.lexer.position))

    # Этот метод обрабатывает инкремент: <increment> ::= <identifier>++
    def increment(self) -> Node:
        if self.token.value != "ID":
            self.error(SyntaxErrors.MissingID(self.lexer.lineno, self.lexer.position))
        
        _id = self.token.name
        self.next_token()

        if self.token.name != "++":
            self.error(SyntaxErrors.MissingSpecSymbol("++", self.lexer.lineno, self.lexer.position))
        self.next_token()

        return NodeIncrement(_id)


    def block(self) -> Node:
        #  Добавляем локальную таблицу символов
        self.symbolTable.append(SymbolTable())

        statements = []
        while self.token.name not in {"}", "break"}:
            statements.append(self.local_statement())

            if isinstance(statements[len(statements) - 1], NodeIfConstruction) or\
                isinstance(statements[len(statements) - 1], NodeWhileConstruction) or\
                isinstance(statements[len(statements) - 1], NodeSwitchConstruction) or\
                isinstance(statements[len(statements) - 1], NodeForConstruction):
                continue

            if self.token.name != ";":
                self.error(SyntaxErrors.MissingSpecSymbol(";", self.lexer.lineno, self.lexer.position))
            self.next_token()
        # Удаляем локальную таблицу символов
        self.symbolTable.pop()
        return NodeBlock(statements)

    # При вызове функции мы уже смотрим на следующий токен
    def formal_params(self) -> Node:
        # Добавляем локальную для метода таблицу символов
        self.symbolTable.append(SymbolTable())
        params = []
        while self.token.name not in {")"}:
            # В params надо добавлять два токена: <type> и <id>.
            # Это и есть наш один формальный параметр.
            params.append(self.declaration())
            if self.token.name != "," and self.token.name != ")":
                self.error(SyntaxErrors.MissingSpecSymbol(",", self.lexer.lineno, self.lexer.position))
            if self.token.name == ",":
                self.next_token()
        # Добавляем локальную таблицу символов аргументы функции
        for i in params:
            self.symbolTable[len(self.symbolTable) - 1].table[i.id] = i.type
        self.next_token()
        return NodeFormalParams(params)

    def local_statement(self) -> Node:
        # Обрабатываем объявление переменных и массивов.
        # Их грамматики:
        # переменные: <type> <id> =? <right_side>?;
        # массивы: <type>[] <id> =? { <constants>? ,? }
        if self.token.name in help.DATA_TYPES:
            return self.declaration()
        # Обрабатываем ситуации, когда меняем значение переменной
        elif self.token.value == "ID":
            id = self.token
            
            # Проверяем на существование переменной
            f = False
            for table in self.symbolTable:
                if self.token.name in table.table:
                    f = True
            if not f:
                expectedWord = self.findExpectedWord(self.token.name)
                self.error(SemanticErrors.UnknowingIdentifier(self.token.name, self.lexer.lineno, self.lexer.position, expectedWord))
            
            self.next_token()

            #  Проверка на знак равенства
            if self.token.name != "=":
                self.error(SyntaxErrors.MissingSpecSymbol("=", self.lexer.lineno, self.lexer.position))
            self.next_token()

            #  Находим тип переменной
            tp = ""
            for table in self.symbolTable:
                if id.name in table.table:
                    tp = table.table[id.name]

            #  Разбираем правую часть
            right = self.expression(tp)

            return NodeAssigning(NodeAtomType(id.name), right)
        # Обрабатываем условия. Их грамматика:
        # if ( <expression> ) { <statements> } else { <statements> }
        elif self.token.name == "if":
            #  Пропускаем if
            self.next_token()

            #  Проверяем наличие (
            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("(", self.lexer.lineno, self.lexer.position))
            #  Пропускаем (
            self.next_token()

            #  Начинаем разбор выражения в скобках
            expr = self.expression("boolean")

            #  Проверяем наличие )
            if self.token.name != ")":
                self.error(SyntaxErrors.MissingSpecSymbol(")", self.lexer.lineno, self.lexer.position))
            #  Пропускаем )
            self.next_token()

            #  Проверяем наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{", self.lexer.lineno, self.lexer.position))
            #  Пропускаем {
            self.next_token()

            #  Начинаем разбор тела условия
            block = self.block()

            # Проверяем наличие }
            if self.token.name != "}":
                self.error(SyntaxErrors.MissingSpecSymbol("}", self.lexer.lineno, self.lexer.position))
            # Пропускаем }
            self.next_token()

            # Проверяем наличие else
            if self.token.name != "else":
                return NodeIfConstruction(expr, block)
            
            # пропускаем else
            self.next_token()

            #  Проверяем наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{", self.lexer.lineno, self.lexer.position))
            self.next_token()

            #  Начинаем разбор тела условия
            else_block = self.block()

            # Проверяем наличие }
            if self.token.name != "}":
                self.error(SyntaxErrors.MissingSpecSymbol("}", self.lexer.lineno, self.lexer.position))
            self.next_token()

            return NodeIfConstruction(expr, block, else_block)
        # Обрабатываем цикл for. Его грамматика:
        # for ( <variable declarator> ; <expression> ; <increment> ) { <statement> }
        elif self.token.name == "for":
            # пропускаем for
            self.next_token()

            #  Проверяем наличие (
            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("(", self.lexer.lineno, self.lexer.position))
            #  Пропускаем (
            self.next_token()

            # Начинаем разбор <variable declarator>
            variable_declarator = self.local_statement()

            #  Проверяем наличие ;
            if self.token.name != ";":
                self.error(SyntaxErrors.MissingSpecSymbol(";", self.lexer.lineno, self.lexer.position))
            #  Пропускаем ;
            self.next_token()

            # Начинаем проверять выражение
            expr = self.expression("boolean")

            #  Проверяем наличие ;
            if self.token.name != ";":
                self.error(SyntaxErrors.MissingSpecSymbol(";", self.lexer.lineno, self.lexer.position))
            #  Пропускаем ;
            self.next_token()

            # Разбираем инкремент
            incr = self.increment()

            # Проверяем, что перменная в объявлении цикла совпадает с переменной в инкременте
            if incr.id != variable_declarator.left_side.id:
                self.error(SemanticErrors.InvalidOperation(self.lexer.lineno, self.lexer.position))

            #  Проверяем наличие )
            if self.token.name != ")":
                self.error(SyntaxErrors.MissingSpecSymbol(")", self.lexer.lineno, self.lexer.position))
            #  Пропускаем )
            self.next_token()

            #  Проверяем наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{", self.lexer.lineno, self.lexer.position))
            #  Пропускаем {
            self.next_token()

            block = self.block()

            # Проверяем наличие }
            if self.token.name != "}":
                self.error(SyntaxErrors.MissingSpecSymbol("}", self.lexer.lineno, self.lexer.position))
            self.next_token()

            return NodeForConstruction(variable_declarator, expr, incr, block)

        # Обрабатываем цикл while. Его грамматика:
        # while ( <expression> ) { <statements> }
        elif self.token.name == "while":
            #  Пропускаем while
            self.next_token()

            #  Проверяем наличие (
            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("(", self.lexer.lineno, self.lexer.position))
            #  Пропускаем (
            self.next_token()

            #  Начинаем разбор выражения в скобках
            expr = self.expression("boolean")

            #  Проверяем наличие )
            if self.token.name != ")":
                self.error(SyntaxErrors.MissingSpecSymbol(")", self.lexer.lineno, self.lexer.position))
            #  Пропускаем )
            self.next_token()

            #  Проверяем наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{", self.lexer.lineno, self.lexer.position))
            #  Пропускаем {
            self.next_token()

            #  Начинаем разбор тела условия
            block = self.block()

            # Проверяем наличие }
            if self.token.name != "}":
                self.error(SyntaxErrors.MissingSpecSymbol("}", self.lexer.lineno, self.lexer.position))
            self.next_token()

            return NodeWhileConstruction(expr, block)
        # Обрабатываем switch statement
        # Гамматика:
        # switch ( <expression> : str, int ) {
            # case value1: <statement> break;
            # case value2: <statement> break;
            # ...
            # default: <statement> break;
        # }
        elif self.token.name == "switch":
            # Список тел блоков case и default
            blocks = list()
            cases = list()
            
            # Пропускаем switch
            self.next_token()
            
            #  Проверяем наличие (
            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("(", self.lexer.lineno, self.lexer.position))
            #  Пропускаем (
            self.next_token()
            
            #  Начинаем разбор выражения в скобках
            if self.token.value != "ID" and\
               self.token.value != "INT" and\
               self.token.value != "STRING":
                self.error(SyntaxErrors.MissingDataType(self.lexer.lineno, self.lexer.position))
            tok = self.token.name
            
            t = ""
            if self.token.value == "ID":
                for table in self.symbolTable:
                    if self.token.name in table.table:
                        t = table.table[self.token.name]
                        break
            else:
                t = self.token.value
            self.next_token()
            
            #  Проверяем наличие )
            if self.token.name != ")":
                self.error(SyntaxErrors.MissingSpecSymbol(")", self.lexer.lineno, self.lexer.position))
            #  Пропускаем )
            self.next_token()
            
            #  Проверяем наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{", self.lexer.lineno, self.lexer.position))
            #  Пропускаем {
            self.next_token()
            
            while self.token.name != "default":
                # Проверяем наличие case
                if self.token.name != "case":
                    self.error(SyntaxErrors.MissingSpecSymbol("case", self.lexer.lineno, self.lexer.position))
                # Пропускаем case
                self.next_token()
                
                # Проверяем тип value
                if self.token.value != "INT" and self.token.value != "STRING":
                    self.error(SyntaxErrors.MissingDataType(self.lexer.lineno, self.lexer.position))
                if self.token.value.lower() != t:
                    self.error(SyntaxErrors.MissingDataType(self.lexer.lineno, self.lexer.position))
                cases.append(self.token)
                # Пропускаем value
                self.next_token()
                
                # Проверяем наличие :
                if self.token.name != ":":
                    self.error(SyntaxErrors.MissingSpecSymbol(":", self.lexer.lineno, self.lexer.position))
                # Пропускаем :
                self.next_token()
                
                # Разбор тела case
                if self.token.name != "break":
                    blocks.append(self.block())
                else:
                    blocks.append("")
                
                # Проверяем наличие break
                if self.token.name != "break":
                    self.error(SyntaxErrors.MissingSpecSymbol("break", self.lexer.lineno, self.lexer.position))
                # Пропускаем break
                self.next_token()
                
                # Проверяем наличие ;
                if self.token.name != ";":
                    self.error(SyntaxErrors.MissingSpecSymbol(";", self.lexer.lineno, self.lexer.position))
                # Пропускаем ;
                self.next_token()
            
            # Пропускаем default
            self.next_token()
            
            # Проверяем наличие :
            if self.token.name != ":":
                self.error(SyntaxErrors.MissingSpecSymbol(":", self.lexer.lineno, self.lexer.position))
            # Пропускаем :
            self.next_token()
            
            # Разбор тела default
            if self.token.name != "break":
                blocks.append(self.block())
            else:
                blocks.append("")
            
            # Проеряем наличие break
            if self.token.name != "break":
                self.error(SyntaxErrors.MissingSpecSymbol("break", self.lexer.lineno, self.lexer.position))
            # Пропускаем break
            self.next_token()
            
            # Проверяем наличие ;
            if self.token.name != ";":
                self.error(SyntaxErrors.MissingSpecSymbol(";", self.lexer.lineno, self.lexer.position))
            # Пропускаем ;
            self.next_token()
            
            # Проверяем наличие }
            if self.token.name != "}":
                self.error(SyntaxErrors.MissingSpecSymbol("}", self.lexer.lineno, self.lexer.position))
            # Пропускаем }
            self.next_token()
            
            return NodeSwitchConstruction(tok, cases, blocks)
        
        # Разбор готовый функций
        # Грамматика:
        # System.out.print(<expression>)
        elif self.token.name == "System.out.print" or self.token.name == "System.out.println":
            # Сохранаяем вид метода
            header = self.token.name

            # Пропускаем System.out.print или System.out.println
            self.next_token()

            # Проверяем (
            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("(", self.lexer.lineno, self.lexer.position))
            self.next_token()

            # Разбор выражения в скобках
            expr = self.expression("boolean")

            # Проверяем )
            if self.token.name != ")":
                self.error(SyntaxErrors.MissingSpecSymbol(")", self.lexer.lineno, self.lexer.position))
            self.next_token()

            return NodeSystemOutPrint(header, expr)

    def statement(self) -> Node:
        # Разбор методов класса, его грамматика:
        # public static <ret_type> <id> ( <formal_params> )
        if self.token.name in help.ACCESS_MODIFIERS:
            # Сохраняем модификатор доступа
            access_mod = self.token.value
            self.next_token()

            # Проверяем ключевое слово static
            if self.token.name not in help.KEY_WORDS:
                self.error(f"Excepted key word: static in line {self.lexer.lineno} on position {self.lexer.position}")
            self.next_token()

            if self.token.name not in help.DATA_TYPES:
                self.error(SyntaxErrors.MissingDataType(self.lexer.lineno, self.lexer.position))
            # Сохраняем возвращаемый тип данных
            ret_type = self.token.value
            self.next_token()

            if self.token.value != "ID":
                self.error(SyntaxErrors.MissingID(self.lexer.lineno, self.lexer.position))
            #  Проверяем не объявлен ли метод повторно
            f = False
            for table in self.symbolTable:
                if self.token.name in table.table:
                    f = True
            if f:
                self.error(SemanticErrors.AlreadyDeclared(self.lexer.lineno, self.lexer.position))
            # Сохраняем имя метода
            _id = self.token.name
            self.next_token()

            # Добавляем нашу функцию в таблицу символов
            self.symbolTable[len(self.symbolTable) - 1].table[_id] = ret_type.lower()

            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("(", self.lexer.lineno, self.lexer.position))
            # Пропускаем круглую скобку
            self.next_token()

            # Начинаем разбор формальных параметров
            formal_params = self.formal_params()
            # Здесь должна быть проверка на наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{", self.lexer.lineno, self.lexer.position))
            # Пропускаем }
            self.next_token()

            # Начинаем разбор тела метода
            block = self.block()

            #  Удаляем таблицу символов блока
            self.symbolTable.pop()

            # Здесь должна быть проверка на наличие '}'
            if self.token.name != "}":
                self.error(SyntaxErrors.MissingSpecSymbol("}", self.lexer.lineno, self.lexer.position))
            # Пропускаем }
            self.next_token()
            return NodeMethod(access_mod, ret_type, _id, formal_params, block)

    def parse(self) -> Node:
        if self.lexer.state == Lexer.EOF:
            self.error("File is empty!")
        else:
            statements = []
            header = ""  # Для заголовка нашего класса
            '''
            Сначала разбираем строку вида: public class <ID> {,
            потому что наш парсер поддерживает только один класс.
            В итоге наш разбор заканчивается на токене следующим за {.
            '''
            if self.token.name not in help.ACCESS_MODIFIERS:
                self.error(f"Missing access modifiers: public in line {self.lexer.lineno} on position {self.lexer.position}")
            self.next_token()
            if self.token.name not in help.KEY_WORDS:
                self.error(f"Missing keyword: class in line {self.lexer.lineno} on position {self.lexer.position}")
            # Запоминаем ключевое слово class
            header += "class "
            self.next_token()
            if self.token.value != "ID":
                self.error(SyntaxErrors.MissingID(self.lexer.lineno, self.lexer.position))
            # Запоминаем название нашего класса
            header += f"{self.token.name} "
            self.next_token()
            if self.token.name not in help.SPEC:
                a = "{"
                self.error(f"Expected '{a}' in line {self.lexer.lineno} on position {self.lexer.position}")
            self.next_token()
            '''
            Потом разбираем остальные инструкции в теле нашего класса
            '''
            while self.lexer.state != Lexer.EOF:
                statements.append(self.statement())
                if self.token.name == "}":
                    self.next_token()
            nodeProgram = NodeProgram(statements)
            nodeProgram.setHeader(header)
            return nodeProgram
        
    def findExpectedWord(self, word) -> str:
                expectedWord = ""
                maxSimilar = 0
                for acc in help.ACCESS_MODIFIERS:
                    sim = similar(str(word), str(acc))
                    if sim > maxSimilar:
                        expectedWord = acc
                        maxSimilar = sim
                for acc in help.KEY_WORDS:
                    sim = similar(str(word), str(acc))
                    if sim > maxSimilar:
                        expectedWord = acc
                        maxSimilar = sim
                for acc in help.DATA_TYPES:
                    sim = similar(str(word), str(acc))
                    if sim > maxSimilar:
                        expectedWord = acc
                        maxSimilar = sim
                return expectedWord

class SemanticErrors:
    @staticmethod
    def UnknowingIdentifier(id, line, pos, expectedWord):
        return f"Using unknowing identifier '{id}' in line {line} on position {pos}. Expected '{expectedWord}'"

    @staticmethod
    def AlreadyDeclared(line, pos):
        return f"Identifier already declared in line {line} on position {pos}"

    @staticmethod
    def TypeMismatch(line, pos):
        return f"Types of operands are different in line {line} on position {pos}"

    @staticmethod
    def InvalidOperation(line, pos):
        return f"Operator do not have declaration for current datatype in line {line} on position {pos}"


class SyntaxErrors:
    @staticmethod
    def DeclarationError(line, pos):
        return f"Declaration error in line {line} on position {pos}"

    @staticmethod
    def MissingID(line, pos):
        return f"Missing identifier in line {line} on position {pos}"

    @staticmethod
    def MissingSpecSymbol(text, line, pos):
        return f"Missing special symbol '{text}' in line {line} on position {pos}"

    @staticmethod
    def MissingDataType(line, pos):
        return f"Missing declaration data type in line {line} on position {pos}"
