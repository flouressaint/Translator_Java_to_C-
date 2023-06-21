from Parser_java import *


def main():
    l = Lexer("./input.txt")
    prs = Parser(l)
    print(prs.parse())


if __name__ == '__main__':
    main()
