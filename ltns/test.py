from compiler import LtnsCompiler
from parser import parser
from lexer import lexer
from pprint import pprint
import ast

test = '''
<print>"Hello World!"</print>
'''

source = parser.parse(lexer.lex(test))

compiler = LtnsCompiler(source)

result = compiler.compile(source[0])

result = ast.fix_missing_locations(result)

eval(compile(ast.Expression(body=result), '<test>', 'eval'))
