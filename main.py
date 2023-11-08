from Parser_java import *


def main():
    l = Lexer("./input.txt")
    prs = Parser(l)
    prs = prs.parse()
    # print(prs)
    cg = CodeGenerator(prs)
    print(cg)


if __name__ == '__main__':
    main()
