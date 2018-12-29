import ast

from .lexer import lexer
from .parser import parser
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


class Result:
    """
    Object that wraps the result

    :param stmts: list of ast.stmt instances that is required to be used as expression
    :param expr: a ast.expr instance that will be handled by other expressions
    """
    def __init__(self, stmts=None, expr=None):
        self.stmts = stmts
        if stmts is None:
            self.stmts = []
        self.expr = expr

    @property
    def expr_statement(self):
        return ast.Expr(value=self.expr)

def ltns_parse(code):
    res = parser.parse(lexer.lex(code))
    return LtnsElement('do', childs=res)

def ltns_compile(tree, filename='<string>'):
    compiler = LtnsCompiler()
    res = compiler.compile(tree)

    res.stmts.append(res.expr_statement)
    body = res.stmts

    tree = ast.Module(body=body)

    ast.fix_missing_locations(tree) # TODO: add location to ast objects

    return compile(tree, filename, 'exec')

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

        result = Result()

        args = []
        keywords = []

        for child in element.childs:
            res = self.compile(child)
            args.append(res.expr)
            result.stmts += res.stmts

        for key, value in element.attributes.items():
            res = self.compile(value)
            keywords.append(ast.keyword(arg=str(key), value=res.expr))
            result.stmts += res.stmts

        expr = ast.Call(func=func, args=args, keywords=keywords)
        result.expr = expr

        return result

    @model(LtnsSymbol)
    def compile_symbol(self, symbol):
        expr = ast.Name(id=str(symbol), ctx=ast.Load())

        return Result(expr=expr)

    @model(LtnsString)
    def compile_string(self, string):
        return Result(expr=ast.Str(str(string)))

    @model(LtnsKeyword)
    def compile_keyword(self, keyword):
        return Result(
            expr=ast.Call(
                func=ast.Name(id='LtnsKeyword', ctx=ast.Load()),
                args=[ast.Str(str(keyword))],
            )
        )

    @model(LtnsInteger)
    def compile_integer(self, integer):
        return Result(expr=ast.Num(int(integer)))

    @model(LtnsFloat)
    def compile_float_number(self, float_number):
        return Result(expr=ast.Num(float(float_number)))

    @model(LtnsComplex)
    def compile_complex_number(self, complex_number):
        return Result(expr=ast.Num(complex(complex_number)))

    @model(LtnsList)
    def compile_list(self, ltns_list):
        result = Result()

        elts = []
        for e in ltns_list:
            res = self.compile(e)
            elts.append(res.expr)
            result.stmts += res.stmts

        expr = ast.List(elts=elts, ctx=ast.Load())
        result.expr = expr

        return result
