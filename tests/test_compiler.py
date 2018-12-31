import ast

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


def compile(tree):
    return LtnsCompiler().compile(tree)

class TestCompiler:
    def test_compile_element(self):
        """<print>"Hello World!"</print>"""
        element = LtnsElement(
            'print',
            childs=[LtnsString('Hello World!')]
        )
        result = compile(element)
        expr = result.expr

        assert not result.stmts

        assert expr.func.id == 'print'
        assert len(expr.args) == 1
        assert expr.args[0].s == 'Hello World!'

    def test_compile_symbol(self):
        """hello"""
        symbol = LtnsSymbol('hello')
        result = compile(symbol)
        expr = result.expr

        assert not result.stmts

        assert expr.id == 'hello'
        assert isinstance(expr.ctx, ast.Load)

    def test_compile_keyword(self):
        """:hello"""
        keyword = LtnsKeyword('hello')
        result = compile(keyword)
        expr = result.expr

        assert not result.stmts

        assert expr.func.id == 'LtnsKeyword'
        assert len(expr.args) == 1
        assert expr.args[0].s == 'hello'

    def test_compile_integer(self):
        """1"""
        integer = LtnsInteger(1)
        result = compile(integer)
        expr = result.expr

        assert not result.stmts

        assert expr.n == 1

    def test_compile_float(self):
        """1.1"""
        float_number = LtnsFloat(1.1)
        result = compile(float_number)
        expr = result.expr

        assert not result.stmts

        assert expr.n == 1.1

    def test_compile_complex(self):
        """1+2j"""
        complex_number = LtnsComplex(1+2j)
        result = compile(complex_number)
        expr = result.expr

        assert not result.stmts

        assert expr.n == 1+2j

    def test_compile_list(self):
        """[1 [1 "nested"]]"""
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

        assert expr.elts[0].n == 1

        assert isinstance(expr.elts[1], ast.List)
        assert isinstance(expr.elts[1].ctx, ast.Load)
        assert len(expr.elts[1].elts) == 1

        assert expr.elts[1].elts[0].s == 'nested'

    def test_bin_op(self):
        """<add*>1 2</add*>"""
        bin_op = LtnsElement(
            name='add*',
            childs=[
                LtnsInteger(1),
                LtnsInteger(2),
            ],
        )
        result = compile(bin_op)
        expr = result.expr

        assert not result.stmts

        assert isinstance(expr.op, ast.Add)

        assert expr.left.n == 1

        assert expr.right.n == 2

    def test_do(self):
        """
        <do>
          <print>"Hello"</print>
          <print>"World!"</print>
        </do>
        """
        do = LtnsElement(
            name='do',
            childs=[
                LtnsElement(
                    name='print',
                    childs=[LtnsString("Hello")],
                ),
                LtnsElement(
                    name='print',
                    childs=[LtnsString("World!")],
                ),
            ],
        )
        result = compile(do)
        expr = result.expr

        assert len(result.stmts) == 1
        assert isinstance(result.stmts[0], ast.Expr)
        assert result.stmts[0].value.args[0].s == 'Hello'

        assert expr.args[0].s == 'World!'

    def test_if_without_stmts(self):
        """<if>True :true :false</if>"""
        tree = LtnsElement(
            name='if',
            childs=[
                LtnsSymbol('True'),
                LtnsKeyword('true'),
                LtnsKeyword('false'),
            ],
        )
        result = compile(tree)
        expr = result.expr

        assert not result.stmts

        assert expr.test.id == 'True'
        assert isinstance(expr.test.ctx, ast.Load)

        assert expr.body.args[0].s == 'true'
        assert expr.orelse.args[0].s == 'false'

    def test_if_with_stmts(self):
        """
        <if>
          True
          <do>1 2</do>
          <do>3 4</do>
        </if>
        """
        tree = LtnsElement(
            name='if',
            childs=[
                LtnsSymbol('True'),
                LtnsElement(
                    name='do',
                    childs=[
                        LtnsInteger(1),
                        LtnsInteger(2),
                    ],
                ),
                LtnsElement(
                    name='do',
                    childs=[
                        LtnsInteger(3),
                        LtnsInteger(4),
                    ],
                ),
            ],
        )
        result = compile(tree)
        expr = result.expr
        stmts = result.stmts

        assert stmts[0].name == '_temp_func_1'
        assert stmts[0].body[0].test.id == 'True'

        assert stmts[0].body[0].body[0].value.n == 1
        assert stmts[0].body[0].body[1].targets[0].id == '_temp_var_2'
        assert stmts[0].body[0].body[1].value.n == 2

        assert stmts[0].body[0].orelse[0].value.n == 3
        assert stmts[0].body[0].orelse[1].targets[0].id == '_temp_var_2'
        assert stmts[0].body[0].orelse[1].value.n == 4

        assert stmts[0].body[1].value.id == '_temp_var_2'

        assert expr.func.id == '_temp_func_1'

    def test_fn_without_stmts(self):
        """<fn*>[x] x</fn*>"""
        fn = LtnsElement(
            name='fn*',
            childs=[
                LtnsList([LtnsSymbol('x')]),
                LtnsSymbol('x'),
            ],
        )
        result = compile(fn)

        assert not result.stmts
        assert result.expr.args.args[0].arg == 'x'
        assert result.expr.body.id == 'x'
