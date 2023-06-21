from Parser_java import *


def main():
    prs = Parser(Lexer("./input.txt")).parse()
    # print(prs)
    cg = CodeGenerator(prs)
    print(cg)


if __name__ == '__main__':
    main()
