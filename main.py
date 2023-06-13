from Parser_java import *


def main():
    prs = Parser(Lexer("./input.txt"))
    print(prs.parse())


if __name__ == '__main__':
    main()
