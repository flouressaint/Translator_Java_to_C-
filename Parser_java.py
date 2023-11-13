import sys
from Lexer_java import Lexer, Token, help
from SymbolTable import SymbolTable
from CodeGenerator import CodeGenerator


class Node:
    def __init__(self, children):
        self.children = children

    def __get_class_name(self):
        c = str(self.__class__)
        pos_1 = c.find('.') + 1
        pos_2 = c.find("'", pos_1)
        return f"{c[pos_1:pos_2]}"

    def __repr__(self, level=0):
        attrs = self.__dict__  # словарь атрибут : значение
        # если атрибут один и тип его значения - это список,
        # то это узел некоторой последовательности (подпрограмма, либо список)
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


class NodeElseBlock(NodeBlock):
    pass


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


class NodeIfConstruction(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block
        #self.else_block = else_block

    def getGeneratedText(self):
        return "if (" + self.condition.getGeneratedText() + ") " + \
               " {\n" + self.block.getGeneratedText() + "}\n"
        #+ self.else_block.getGeneratedText()


class NodeWhileConstruction(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def getGeneratedText(self):
        return "while (" + self.condition.getGeneratedText() + ") " + self.block.getGeneratedText()


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
        return self.id + " "


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


class NodeUnaryMinus(NodeUnaryOperator):
    def getGeneratedText(self):
        return "-" + self.operand.getGeneratedText()


class NodeNot(NodeUnaryOperator):
    def getGeneratedText(self):
        return "!" + self.operand.getGeneratedText()


class NodeBinaryOperator(Node):
    def __init__(self, left, right, operator=""):
        self.left = left
        self.right = right
        self.operator = operator

    def getGeneratedText(self):
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
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = self.lexer.get_next_token()
        self.symbolTable = list()
        self.symbolTable.append(SymbolTable())

    def next_token(self):
        self.token = self.lexer.get_next_token()

    def error(self, msg):
        print(f'Ошибка синтаксического анализа ({self.lexer.pos}): {msg}')
        sys.exit(1)

    def operand(self, _type) -> Node:
        first_token = self.token
        # Определяем тип операнда
        if self.token.value.lower() == "int":
            self.next_token()
            return NodeIntLiteral(first_token.name, first_token.value.lower())
        elif self.token.value.lower() == "double":
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
                self.error(SemanticErrors.UnknowingIdentifier())
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
    # А именно выражение с операциями * и /.
    def term(self, _type) -> Node:
        left = self.factor(_type)
        op = self.token.name
        while op in {"*", "/", "<", ">", "==", "&&"}:
            self.next_token()
            if op == "*":
                right = self.factor(_type)
                left = NodeMultiply(left, right)
            elif op == "/":
                right = self.factor(_type)
                left = NodeDivision(left, right)
            elif op == ">":
                right = self.factor(_type)
                left = NodeG(left, right)
            elif op == "<":
                right = self.factor(_type)
                left = NodeL(left, right)
            elif op == "==":
                right = self.factor(_type)
                left = NodeEQ(left, right)
            elif op == "&&":
                left = NodeAnd(left, self.term(_type))
            op = self.token.name
        return left

    # Этот метод обрабатывает арифметические выражения.
    # А именно выражения с операциями + и -.
    def expression(self, _type) -> Node:
        left = self.term(_type)
        op = self.token.name
        while op in {"+", "-", "||"}:
            self.next_token()
            if op == "+":
                left = NodePlus(left, self.term(_type))
            elif op == "-":
                left = NodeMinus(left, self.term(_type))
            elif op == "||":
                left = NodeOr(left, self.term(_type))
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
                self.error(SemanticErrors.AlreadyDeclared())
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
                    return NodeAssigning(left_side, right_side)
            # Добавляем переменную в таблицу символов
            self.symbolTable[len(self.symbolTable) - 1].table[_id] = data_type
            return NodeDeclaration(data_type, _id)
        # Обрабатываем объявление массивов.
        elif self.token.name == "[":
            self.next_token()
            if self.token.name != "]":
                self.error(SyntaxErrors.MissingSpecSymbol("]"))
            self.next_token()
            if self.token.value != "ID":
                self.error(SyntaxErrors.MissingID())
            _id = self.token.name
            self.next_token()
        else:
            self.error(SyntaxErrors.DeclarationError())

    def block(self) -> Node:
        #  Добавляем локальную таблицу символов
        self.symbolTable.append(SymbolTable())

        statements = []
        while self.token.name not in {"}"}:
            statements.append(self.local_statement())
            if self.token.name != "}" and self.token.name != ";":
                self.error(SyntaxErrors.MissingSpecSymbol(";"))
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
                self.error(SyntaxErrors.MissingSpecSymbol(","))
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
            self.next_token()

            #  Проверка на знак равенства
            if self.token.name != "=":
                self.error(SyntaxErrors.MissingSpecSymbol("="))
            self.next_token()

            #  Находим тип переменной
            tp = ""
            f = False
            for table in self.symbolTable:
                if id.name in table.table:
                    tp = table.table[id.name]
                    f = True

            #  Разбираем правую часть
            right = self.expression(tp)

            return NodeAssigning(NodeAtomType(id.name), right)
        # Обрабатываем условия. Их грамматика:
        # if ( <expression> ) { <statements> }
        elif self.token.name == "if":
            #  Пропускаем if
            self.next_token()

            #  Проверяем наличие (
            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("("))
            #  Пропускаем (
            self.next_token()

            #  Начинаем разбор выражения в скобках
            expr = self.expression("boolean")

            #  Проверяем наличие )
            if self.token.name != ")":
                self.error(SyntaxErrors.MissingSpecSymbol(")"))
            #  Пропускаем )
            self.next_token()

            #  Проверяем наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{"))
            #  Пропускаем {
            self.next_token()

            #  Начинаем разбор тела условия
            block = self.block()

            #  Проверяем наличие }
            #if self.token.name != "}":
             #   self.error(SyntaxErrors.MissingSpecSymbol("}"))
            #  Пропускаем }
            #self.next_token()

            return NodeIfConstruction(expr, block)
        # Обрабатываем цикл while. Его грамматика:
        # while ( <expression> ) { <statements> }
        elif self.token.name == "while":
            pass

    def statement(self) -> Node:
        # Разбор методов класса, его грамматика:
        # public static <ret_type> <id> ( <formal_params> )
        if self.token.name in help.ACCESS_MODIFIERS:
            # Сохраняем модификатор доступа
            access_mod = self.token.value
            self.next_token()

            # Проверяем ключевое слово static
            if self.token.name not in help.KEY_WORDS:
                self.error("Excepted key word: static")
            self.next_token()

            if self.token.name not in help.DATA_TYPES:
                self.error(SyntaxErrors.MissingDataType())
            # Сохраняем возвращаемый тип данных
            ret_type = self.token.value
            self.next_token()

            if self.token.value != "ID":
                self.error(SyntaxErrors.MissingID())
            #  Проверяем не объявлен ли метод повторно
            f = False
            for table in self.symbolTable:
                if self.token.name in table.table:
                    f = True
            if f:
                self.error(SemanticErrors.AlreadyDeclared())
            # Сохраняем имя метода
            _id = self.token.name
            self.next_token()

            # Добавляем нашу функцию в таблицу символов
            self.symbolTable[len(self.symbolTable) - 1].table[_id] = ret_type.lower()

            if self.token.name != "(":
                self.error(SyntaxErrors.MissingSpecSymbol("("))
            # Пропускаем круглую скобку
            self.next_token()

            # Начинаем разбор формальных параметров
            formal_params = self.formal_params()
            # Здесь должна быть проверка на наличие {
            if self.token.name != "{":
                self.error(SyntaxErrors.MissingSpecSymbol("{"))
            # Пропускаем }
            self.next_token()

            # Начинаем разбор тела метода
            block = self.block()
            #  Удаляем таблицу символов блока
            self.symbolTable.pop()

            # Здесь должна быть проверка на наличие '}'
            if self.token.name != "}":
                self.error(SyntaxErrors.MissingSpecSymbol("}"))
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
                self.error("Missing access modifiers: public")
            self.next_token()
            if self.token.name not in help.KEY_WORDS:
                self.error("Missing keyword: class")
            # Запоминаем ключевое слово class
            header += "class "
            self.next_token()
            if self.token.value != "ID":
                self.error(SyntaxErrors.MissingID())
            # Запоминаем название нашего класса
            header += f"{self.token.name} "
            self.next_token()
            if self.token.name not in help.SPEC:
                self.error("Expected '{'")
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


class SemanticErrors:
    @staticmethod
    def UnknowingIdentifier():
        return "Using unknowing identifier"

    @staticmethod
    def AlreadyDeclared():
        return "Identifier already declared"

    @staticmethod
    def TypeMismatch():
        return "Types of operands are different"


class SyntaxErrors:
    @staticmethod
    def DeclarationError():
        return "Declaration error"

    @staticmethod
    def MissingID():
        return "Missing identifier"

    @staticmethod
    def MissingSpecSymbol(text):
        return "Missing special symbol {}".format(text)

    @staticmethod
    def MissingDataType():
        return "Missing declaration data type"
