import ast

from ltns.compiler import LtnsCompiler
from ltns.parser import parser
from ltns.lexer import lexer

test = '''
<print>"Hello World!"</print>
'''

source = parser.parse(lexer.lex(test))

compiler = LtnsCompiler()

result = compiler.compile(source[0])

result = ast.fix_missing_locations(result)

eval(compile(ast.Expression(body=result), '<test>', 'eval'))
