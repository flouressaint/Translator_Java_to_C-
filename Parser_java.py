import sys
from Lexer_java import Lexer, Token, help


class Node:
    def __get_class_name(self):
        c = str(self.__class__)
        pos_1 = c.find('.') + 1
        pos_2 = c.find("'", pos_1)
        return f"{c[pos_1:pos_2]}"

    def __repr__(self, level=0):
        attrs = self.__dict__  # словарь атрибут: значение
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
                res += '|+-'
                res += el.__repr__(level + 1)
        else:
            for attr_name in attrs:
                res += '|   ' * level
                res += '|+-'
                if isinstance(attrs[attr_name], Token):
                    res += f"{attr_name}: {attrs[attr_name]}\n"
                else:
                    res += f"{attr_name}: {attrs[attr_name].__repr__()}\n"
        return res


class NodeProgram(Node):
    def __init__(self, children):
        self.children = children


class NodeBlock(NodeProgram):
    pass


class NodeElseBlock(NodeBlock):
    pass


class NodeDeclaration(Node):
    def __init__(self, _type, _id):
        self.type = _type
        self.id = _id


class NodeAssigning(Node):
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side


class NodeMethod(Node):
    def __init__(self, access_mod, ret_type, _id, formal_params, block):
        self.access_mod = access_mod
        self.ret_type = ret_type
        self.id = _id
        self.formal_params = formal_params
        self.block = block


class NodeSequence(Node):
    def __init__(self, members):
        self.members = members


class NodeParams(Node):
    def __init__(self, params):
        self.params = params


class NodeFormalParams(NodeParams):
    pass


class NodeActualParams(NodeParams):
    pass


class NodeIfConstruction(Node):
    def __init__(self, condition, block, else_block):
        self.condition = condition
        self.block = block
        self.else_block = else_block


class NodeWhileConstruction(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block


class NodeReturnStatement(Node):
    def __init__(self, expression):
        self.expression = expression


class NodeLiteral(Node):
    def __init__(self, value):
        self.value = value


class NodeStringLiteral(NodeLiteral):
    pass


class NodeIntLiteral(NodeLiteral):
    pass


class NodeFloatLiteral(NodeLiteral):
    pass


class NodeVar(Node):
    def __init__(self, _id):
        self.id = _id


class NodeAtomType(Node):
    def __init__(self, _id):
        self.id = _id


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


class NodeUnaryMinus(NodeUnaryOperator):
    pass


class NodeNot(NodeUnaryOperator):
    pass


class NodeBinaryOperator(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class NodeL(NodeBinaryOperator):
    pass


class NodeG(NodeBinaryOperator):
    pass


class NodeLE(NodeBinaryOperator):
    pass


class NodeGE(NodeBinaryOperator):
    pass


class NodeEQ(NodeBinaryOperator):
    pass


class NodeNEQ(NodeBinaryOperator):
    pass


class NodeOr(NodeBinaryOperator):
    pass


class NodeAnd(NodeBinaryOperator):
    pass


class NodePlus(NodeBinaryOperator):
    pass


class NodeMinus(NodeBinaryOperator):
    pass


class NodeDivision(NodeBinaryOperator):
    pass


class NodeMultiply(NodeBinaryOperator):
    pass


class NodeIDivision(NodeBinaryOperator):
    pass


class NodeMod(NodeBinaryOperator):
    pass


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = self.lexer.get_next_token()

    def next_token(self):
        self.token = self.lexer.get_next_token()

    def error(self, msg):
        print(f'Ошибка синтаксического анализа ({self.lexer.pos}): {msg}')
        sys.exit(1)

    # Этот метод обрабатывает выражения
    def expression(self) -> Node:
        pass

    # Этот метод обрабатывает пары токенов вида: <type> <id>
    def declaration(self) -> Node:
        if self.token.name not in help.DATA_TYPES:
            self.error(MissingDataType.report())
        _type = self.token.value
        self.next_token()

        if self.token.value != "ID":
            self.error(MissingID.report())
        _id = self.token.name
        self.next_token()

        if self.token.name == "=":
            right_side = self.expression()
            return NodeAssigning(NodeDeclaration(_type, _id), right_side)
        return NodeDeclaration(_type, _id)

    def block(self) -> Node:
        statements = []
        while self.token.name not in {"}"}:
            statements.append(self.statement())
            if self.token.name != ";":
                self.error(MissingSpecSybmol.report(";"))
            self.next_token()
        return NodeBlock(statements)

    # При вызове функции мы уже смотрим на следующий токен
    def formal_params(self) -> Node:
        params = []
        while self.token.name not in {")"}:
            # В params надо добавлять два токена: <type> и <id>.
            # Это и есть наш один формальный параметр.
            params.append(self.declaration())
            if self.token.name != "," and self.token.name != ")":
                self.error(MissingSpecSybmol.report(","))
            if self.token.name == ",":
                self.next_token()
        self.next_token()
        return NodeFormalParams(params)

    def statement(self) -> Node:
        # Разбор методов класса, его грамматика:
        # public <ret_type> <id> ( <formal_params> )
        if self.token.name in help.ACCESS_MODIFIERS:
            # Сохраняем модификатор доступа
            access_mod = self.token.value
            self.next_token()

            # Проверяем ключевое слово static
            if self.token.name not in help.KEY_WORDS:
                self.error("Excepted key word: static")
            self.next_token()

            if self.token.name not in help.DATA_TYPES:
                self.error(MissingDataType.report())
            # Сохраняем возвращаемый тип данных
            ret_type = self.token.value
            self.next_token()

            if self.token.value != "ID":
                self.error(MissingID.report())
            # Сохраняем имя метода
            _id = self.token.name
            self.next_token()

            if self.token.name != "(":
                self.error(MissingSpecSybmol.report("("))
            # Пропускаем круглую скобку
            self.next_token()

            # Начинаем разбор формальных параметров
            formal_params = self.formal_params()
            # Здесь должна быть проверка на наличие {
            if self.token.name != "{":
                self.error(MissingSpecSybmol.report("{"))
            # Пропускаем }
            self.next_token()

            # Начинаем разбор тела метода
            block = self.block()
            # Здесь должна быть проверка на наличие }
            if self.token.name != "}":
                self.error(MissingSpecSybmol.report("}"))
            # Пропускаем }
            self.next_token()
            return NodeMethod(access_mod, ret_type, _id, formal_params, block)

    def parse(self) -> Node:
        if self.lexer.state == Lexer.EOF:
            self.error("File is empty!")
        else:
            statements = []
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
            self.next_token()
            if self.token.value != "ID":
                self.error(MissingID.report())
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
            return NodeProgram(statements)


class MissingID:
    @staticmethod
    def report():
        return "Missing identifier"


class MissingSpecSybmol:
    @staticmethod
    def report(text):
        return "Missing special symbol {}".format(text)


class MissingDataType:
    @staticmethod
    def report():
        return "Missing declaration data type"
