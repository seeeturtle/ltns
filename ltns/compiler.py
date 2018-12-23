import ast

from .models import (
    LtnsElement,
    LtnsKeyword,
    LtnsString,
    LtnsSymbol,
    LtnsInteger,
    LtnsFloat,
    LtnsComplex,
    LtnsList,
)

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

    @model(LtnsKeyword)
    def compile_keyword(self, keyword):
        return ast.Call(
            func = ast.Name(id='LtnsKeyword', ctx=ast.Load()),
            args=[self.compile(LtnsString(keyword.value))],
        )

    @model(LtnsInteger)
    def compile_integer(self, integer):
        return ast.Num(int(integer))

    @model(LtnsFloat)
    def compile_float_number(self, float_number):
        return ast.Num(float(float_number))

    @model(LtnsComplex)
    def compile_complex_number(self, complex_number):
        return ast.Num(complex(complex_number))

    @model(LtnsList)
    def comiler_list(self, ltns_list):
        return ast.List(
            elts=[self.compile(e) for e in ltns_list],
            ctx=ast.Load(),
        )
