import ast
from functools import partial

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

_special_form_compiler = {}

def special(name, args=['name', 'childs', 'attrs']):
    def decorator(f):
        _special_form_compiler[name] = f
        return f
    return decorator

class LtnsCompiler:
    def _temp_func_name(self):
        if not hasattr(self, '_temp'):
            self._temp = 0
        self._temp += 1
        return f'_temp_func_{self._temp}'

    def _temp_var_name(self):
        if not hasattr(self, '_temp'):
            self._temp = 0
        self._temp += 1
        return f'_temp_var_{self._temp}'

    def _compile_branch(self, branch):
        result = Result()

        for x in branch[:-1]:
            res = self.compile(x)
            result.stmts += res.stmts
            result.stmts += [res.expr_statement]

        res = self.compile(branch[-1])
        result.stmts += res.stmts
        result.expr = res.expr

        return result

    def _compile_args(self, args, kwargs):
        for i, arg in enumerate(args):
            if arg == '&':
                vararg = ast.arg(str(args[i+1], None), None)
                posarg = args[:i]
        else:
            vararg = None
            posarg = args

        return ast.arguments(
            args=[ast.arg(str(x), None) for x in posarg],
            vararg=vararg,
            kwonlyargs=[ast.arg(str(x), None) for x in kwargs],
            kwarg=None,
            defaults=[],
            kw_defaults=list(kwargs.values()),
        )

    def compile(self, node):
        return _model_compiler[type(node)](self, node)

    @model(LtnsElement)
    def compile_element(self, element):
        if element.name in _special_form_compiler:
            return _special_form_compiler[element.name](
                self, *element.childs, **element.attributes
            )

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

    @special('do')
    def compile_do(self, *body):
        return self._compile_branch(body)

    name_op = {
        'add*': ast.Add(),
        'sub*': ast.Sub(),
        'mul*': ast.Mult(),
        'div*': ast.Div(),
        'mod': ast.Mod(),
        'pow': ast.Pow(),
        'lshift': ast.LShift(),
        'rshift': ast.RShift(),
        'bitor': ast.BitOr(),
        'bitxor': ast.BitXor(),
        'bitand': ast.BitAnd(),
    }

    def compile_bin_op(self, a, b, name):
        result = Result()

        left = self.compile(a)
        result.stmts += left.stmts
        left = left.expr

        right = self.compile(b)
        result.stmts += right.stmts
        right = right.expr

        expr = ast.BinOp(op=self.name_op[name], left=left, right=right)
        result.expr = expr

        return result

    for name in name_op:
        _special_form_compiler[name] = partial(compile_bin_op, name=name)

    @special('if')
    def compile_if(self, test, then, orelse=None):
        result = Result()

        pred = self.compile(test)
        result.stmts += pred.stmts

        then_body = self.compile(then)

        else_body = None
        if orelse is not None:
            else_body = self.compile(orelse)

        if then_body.stmts or else_body.stmts:
            temp_func_name = self._temp_func_name()
            temp_var_name = self._temp_var_name()

            body = then_body.stmts
            body.append(
                ast.Assign(
                    targets=[ast.Name(id=temp_var_name, ctx=ast.Store())],
                    value=then_body.expr,
                )
            )

            orelse = else_body.stmts
            orelse.append(
                ast.Assign(
                    targets=[ast.Name(id=temp_var_name, ctx=ast.Store())],
                    value=else_body.expr,
                )
            )

            result.stmts.append(
                ast.FunctionDef(
                    name=temp_func_name,
                    args=ast.arguments(
                        args=[],
                        vararg=None,
                        kwonlyargs=[],
                        kw_defaults=[],
                        kwarg=None,
                        defaults=[],
                    ),
                    body=[
                        ast.If(test=pred.expr, body=body, orelse=orelse),
                        ast.Return(value=ast.Name(id=temp_var_name, ctx=ast.Load())),
                    ],
                    decorator_list=[],
                    returns=None,
                )
            )

            result.expr = ast.Call(
                func=ast.Name(id=temp_func_name, ctx=ast.Load()),
                args=[],
                keywords=[],
            )

            return result
        else:
            result.expr = ast.IfExp(
                test=pred.expr,
                body=then_body.expr,
                orelse=else_body.expr,
            )

            return result

    @special('fn*')
    def compile_fn(self, args, *body, **kwargs):
        result = Result()

        body = self._compile_branch(body)
        args = self._compile_args(args, kwargs)

        if body.stmts:
            fdef = ast.FunctionDef()
            fdef.name = self._temp_func_name()
            fdef.args = args
            fdef.body = body.stmts + [ast.Return(body.expr)]
            fdef.decorator_list = []
            fdef.returns = None

            result.stmts += [fdef]
            result.expr = ast.Name(id=fdef.name, ctx=ast.Load())
        else:
            result.expr = ast.Lambda(args=args, body=body.expr)

        return result
