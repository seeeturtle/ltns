from functools import reduce


class LtnsObject:
    def __init__(self, token, **kwargs):
        self.lineno = token.getsourcepos().lineno - 1
        self.col_offset = token.getsourcepos().colno - 1

class LtnsElement(LtnsObject):
    def __init__(self, name, start_token, **kwargs):
        self.name = name
        self.attributes = kwargs.pop('attributes', {})
        self.childs = kwargs.pop('childs', [])

        super().__init__(start_token, **kwargs)

class LtnsInteger(LtnsObject, int):
    def __new__(cls, token, **kwargs):
        return super().__new__(cls, token.getstr(), **kwargs)

class LtnsFloat(float):
    def __new__(cls, token, **kwargs):
        return super().__new__(cls, token.getstr(), **kwargs)

class LtnsComplex(LtnsObject, complex):
    def __new__(cls, token, **kwargs):
        return super().__new__(cls, token.getstr(), **kwargs)

class LtnsKeyword(LtnsObject):
    def __init__(self, token, **kwargs):
        if not token.getstr().startswith(':'):
            raise ValueError
        self.value = token.getstr()

        super().__init__(token, **kwargs)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return reduce(
            lambda x, y: 1/2*(x+y)*(x+y+1)+y,
            (ord(c) for c in self.value))

class LtnsString(LtnsObject, str):
    def __new__(cls, token, **kwargs):
        return super().__new__(cls, token.getstr()[1:-1], **kwargs)

class LtnsSymbol(LtnsObject):
    def __init__(self, token, **kwargs):
        self.name = token.getstr()

        super().__init__(token, **kwargs)

    def __hash__(self):
        return self.name
