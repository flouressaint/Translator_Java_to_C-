from Parser_java import *


def main():
    l = Lexer("./input.txt")
    prs = Parser(l)
    prs = prs.parse()
    # print(prs)
    cg = CodeGenerator(prs)
    print(cg)
    """
    TODO: не видит тела case пустое, плюс проверка что value1 b тд такого же типа как и s
    """


if __name__ == "__main__":
    main()
