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

_special_form_compiler = {}

def special(name, args=['name', 'childs', 'attrs']):
    def decorator(f):
        _special_form_compiler[name] = (f, args)
        return f
    return decorator

class LtnsCompiler:
    _temp = 0

    def _temp_func_name(self):
        self._temp += 1
        return f'_temp_func_{self._temp}'

    def _temp_var_name(self):
        self._temp += 1
        return f'_temp_var_{self._temp}'

    def compile(self, node):
        return _model_compiler[type(node)](self, node)

    @model(LtnsElement)
    def compile_element(self, element):
        if element.name in _special_form_compiler:
            sf, args = _special_form_compiler[element.name]

            data = {
                'name': element.name,
                'childs': element.childs,
                'attrs': element.attributes,
            }
            args = [data[arg] for arg in args]

            return sf(self, *args)

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

    @special('do', ['childs'])
    def compile_do(self, childs):
        result = Result()

        childs = [self.compile(child) for child in childs]

        for child in childs[:-1]:
            result.stmts += child.stmts
            result.stmts.append(child.expr_statement)

        expr = childs[-1].expr
        result.stmts += childs[-1].stmts
        result.expr = expr

        return result

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

    def compile_bin_op(self, name, childs):
        result = Result()

        left = self.compile(childs[0])
        result.stmts += left.stmts
        left = left.expr

        right = self.compile(childs[1])
        result.stmts += right.stmts
        right = right.expr

        expr = ast.BinOp(op=self.name_op[name], left=left, right=right)
        result.expr = expr

        return result

    for name in name_op:
        _special_form_compiler[name] = (compile_bin_op, ['name', 'childs'])

    @special('if', ['childs'])
    def compile_if(self, childs):
        result = Result()

        pred = self.compile(childs[0])
        result.stmts += pred.stmts

        then_body = self.compile(childs[1])

        try:
            else_body = self.compile(childs[2])
        except IndexError:
            else_body = None

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
