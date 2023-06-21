class CodeGenerator:
    def __init__(self, source):
        self.source = source

    def __repr__(self) -> str:
        return self.source.headerProgram + "\n{\n" + self.source.getGeneratedText() + "}"
