from functools import reduce

class LtnsElement:
    def __init__(self, name, **kwargs):
        self.name = name
        self.attributes = kwargs.pop('attributes', {})
        self.childs = kwargs.pop('childs', [])

# class LtnsInteger(int):
#     def __new__(cls, x, **kwargs):
#         return super(LtnsInteger, cls).__new__(cls, x, **kwargs)

# class LtnsFloat(float):
#     def __new__(cls, x, **kwargs):
#         return super(LtnsFloat, cls).__new__(cls, x, **kwargs)

# class LtnsComplex(complex):
#     def __new__(cls, x, **kwargs):
#         return super(LtnsComplex, cls).__new__(cls, x, **kwargs)

class LtnsKeyword:
    def __init__(self, value, **kwargs):
        if not value.startswith(':'):
            raise ValueError
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return reduce(
            lambda x, y: 1/2*(x+y)*(x+y+1)+y,
            (ord(c) for c in self.value))

# class LtnsString(str):
#     def __new__(cls, s, **kwargs):
#         return super(LtnsString, cls).__new__(cls, s, **kwargs)
