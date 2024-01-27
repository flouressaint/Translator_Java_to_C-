from Parser_java import *


def main():
    l = Lexer("./input.txt")
    print("\n-------------------ИСХОДНАЯ ПРОГРАММА НА JAVA------------------------")
    with open("./input.txt") as f:
        # print file
        print(f.read())
    prs = Parser(l)
    prs = prs.parse()
    cg = CodeGenerator(prs)
    print("\n-------------------------ПРОГРАММА НА C#----------------------------")
    print(cg)

    print("\n-------------------------ДЕРЕВО РАЗБОРА----------------------------")
    print(prs)



if __name__ == "__main__":
    main()
