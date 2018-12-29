from ltns.compiler import LtnsCompiler
from ltns.compiler import ltns_parse
from ltns.models import (
    LtnsElement,
    LtnsSymbol,
    LtnsString,
    LtnsKeyword,
    LtnsInteger,
    LtnsFloat,
    LtnsComplex,
    LtnsList,
)

import ast

def compile(tree):
    return LtnsCompiler().compile(tree)

class TestCompiler:
    def test_compile_element(self):
        element = LtnsElement(
            'print',
            childs=[LtnsString('Hello World!')]
        )
        result = compile(element)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr, ast.Call)
        assert expr.func.id == 'print'
        assert len(expr.args) == 1
        assert isinstance(expr.args[0], ast.Str)
        assert expr.args[0].s == 'Hello World!'

    def test_compile_symbol(self):
        symbol = LtnsSymbol('hello')
        result = compile(symbol)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr, ast.Name)
        assert expr.id == 'hello'
        assert isinstance(expr.ctx, ast.Load)

    def test_compile_keyword(self):
        keyword = LtnsKeyword('hello')
        result = compile(keyword)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr, ast.Call)
        assert isinstance(expr.func, ast.Name)
        assert expr.func.id == 'LtnsKeyword'
        assert len(expr.args) == 1
        assert isinstance(expr.args[0], ast.Str)
        assert expr.args[0].s == 'hello'

    def test_compile_integer(self):
        integer = LtnsInteger(1)
        result = compile(integer)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr, ast.Num)
        assert expr.n == 1

    def test_compile_float(self):
        float_number = LtnsFloat(1.1)
        result = compile(float_number)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr, ast.Num)
        assert expr.n == 1.1

    def test_compile_complex(self):
        complex_number = LtnsComplex(1+2j)
        result = compile(complex_number)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr, ast.Num)
        assert expr.n == 1+2j

    def test_compile_list(self):
        ltns_list = LtnsList([
            LtnsInteger(1),
            LtnsList([LtnsString('nested')]),
        ])
        result = compile(ltns_list)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr, ast.List)
        assert isinstance(expr.ctx, ast.Load)
        assert len(expr.elts) == 2

        assert isinstance(expr.elts[0], ast.Num)
        assert expr.elts[0].n == 1

        assert isinstance(expr.elts[1], ast.List)
        assert isinstance(expr.elts[1].ctx, ast.Load)
        assert len(expr.elts[1].elts) == 1

        assert isinstance(expr.elts[1].elts[0], ast.Str)
        assert expr.elts[1].elts[0].s == 'nested'


        assert isinstance(result.elts[0], ast.Num)
        assert result.elts[0].n == 1

        assert isinstance(result.elts[1], ast.List)
        assert isinstance(result.elts[1].ctx, ast.Load)
        assert len(result.elts[1].elts) == 1

        assert isinstance(result.elts[1].elts[0], ast.Str)
        assert result.elts[1].elts[0].s == 'nested'
