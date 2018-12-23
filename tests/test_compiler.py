from ltns.compiler import LtnsCompiler
from ltns.models import (
    LtnsElement,
    LtnsSymbol,
    LtnsString,
    LtnsKeyword,
    LtnsInteger,
    LtnsFloat,
    LtnsComplex,
)

import ast


class TestCompiler:
    def test_compile_element(self):
        element = LtnsElement(
            'print',
            childs=[LtnsString('Hello World!')]
        )
        result = LtnsCompiler().compile(element)

        assert isinstance(result, ast.Call)
        assert result.func.id == 'print'
        assert len(result.args) == 1
        assert isinstance(result.args[0], ast.Str)
        assert result.args[0].s == 'Hello World!'

    def test_compile_symbol(self):
        symbol = LtnsSymbol('hello')
        result = LtnsCompiler().compile(symbol)

        assert isinstance(result, ast.Name)
        assert result.id == 'hello'
        assert isinstance(result.ctx, ast.Load)

    def test_compile_keyword(self):
        keyword = LtnsKeyword('hello')
        result = LtnsCompiler().compile(keyword)

        assert isinstance(result, ast.Call)
        assert isinstance(result.func, ast.Name)
        assert result.func.id == 'LtnsKeyword'
        assert len(result.args) == 1
        assert isinstance(result.args[0], ast.Str)
        assert result.args[0].s == 'hello'

    def test_compile_integer(self):
        integer = LtnsInteger(1)
        result = LtnsCompiler().compile(integer)

        assert isinstance(result, ast.Num)
        assert result.n == 1

    def test_compile_float(self):
        float_number = LtnsFloat(1.1)
        result = LtnsCompiler().compile(float_number)

        assert isinstance(result, ast.Num)
        assert result.n == 1.1

    def test_compile_complex(self):
        complex_number = LtnsComplex(1+2j)
        result = LtnsCompiler().compile(complex_number)

        assert isinstance(result, ast.Num)
        assert result.n == 1+2j
