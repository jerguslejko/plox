class RealPrinter:
    def print(self, *values):
        print(*values)

    def get(self):
        raise ValueError("[real printer] cannot get output")


class FakePrinter:
    def __init__(self):
        self.buffer = []

    def print(self, value):
        self.buffer.append(value)

    def get(self):
        return self.buffer
