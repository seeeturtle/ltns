import ast

from models import LtnsElement, LtnsKeyword, LtnsString, LtnsSymbol

_model_compiler = {}

def model(node_type):
    def decorator(f):
        _model_compiler[node_type] = f
        return f
    return decorator

class LtnsCompiler:
    def compile(self, node):
        return _model_compiler[type(node)](self, node)

    @model(LtnsElement)
    def compile_element(self, element):
        func = ast.parse(element.name, mode='eval').body # TODO: handle exception of parsing

        return ast.Call(
            func=func,
            args=[self.compile(child) for child in element.childs],
            keywords=[ast.keyword(
                arg=key.name,
                value=self.compile(value),
            ) for key, value in element.attributes.items()],
        )

    @model(LtnsSymbol)
    def compile_symbol(self, symbol):
        return ast.Name(id=symbol.name, ctx=ast.Load())

    @model(LtnsString)
    def compile_string(self, string):
        return ast.Str(str(string))
