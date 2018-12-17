from collections import namedtuple

from rply import ParserGenerator

from lexer import lexer
from models import (
    LtnsElement,
    LtnsKeyword,
    LtnsSymbol,
    LtnsString,
)


pg = ParserGenerator([rule.name for rule in lexer.rules] + ['end$'])

tag = namedtuple('tag', ('name', 'attributes'))

@pg.production("main : list_contents")
def main(p):
    return p[0]

@pg.production("main : end$")
def main_empty(_):
    return []

@pg.production("list_contents : term list_contents")
def list_contents(p):
    return [p[0]] + p[1]

@pg.production("list_contents : term")
def list_contents_term(p):
    return [p[0]]

@pg.production("term : element")
@pg.production("term : identifier")
@pg.production("term : string")
def term(p):
    return p[0]

@pg.production("element : start_tag list_contents end_tag")
def element(p):
    return LtnsElement(p[0].name, attributes=p[0].attributes, childs=p[1])

@pg.production("element : start_tag end_tag")
@pg.production("element : empty_tag")
def empty_element(p):
    return LtnsElement(p[0].name, attributes=p[0].attributes)

@pg.production("start_tag : LANGLE identifier attributes RANGLE")
def start_tag(p):
    return tag(p[1].name, p[2])

@pg.production("start_tag : LANGLE identifier RANGLE")
def start_tag_without_attributes(p):
    return tag(p[1].name, {})

@pg.production("attributes : identifier EQUAL term attributes")
def attributes(p):
    d = {p[0].name: p[2]}
    d.update(p[3])

    return d

@pg.production("attributes : identifier EQUAL term")
def attributes_one(p):
    return {p[0].name: p[2]}

@pg.production("end_tag : LSLASHANGLE identifier RANGLE")
def end_tag(p):
    return tag(p[1].name, None)

@pg.production("empty_tag : LANGLE identifier attributes RSLASHANGLE")
def empty_tag(p):
    return tag(p[1].name, p[2])

@pg.production("identifier : IDENTIFIER")
def identifier(p):
    try:
        return int(p[0].getstr())
    except ValueError:
        pass

    try:
        return float(p[0].getstr())
    except ValueError:
        pass

    try:
        return complex(p[0].getstr())
    except ValueError:
        pass

    try:
        return LtnsKeyword(p[0].getstr())
    except ValueError:
        pass

    return LtnsSymbol(p[0].getstr())

@pg.production("string : STRING")
def string(p):
    return LtnsString(p[0].getstr())

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

parser = pg.build()

# test = '''
# <let
#   square = <->2 1</->
#   y = <+>1 2</+>
# />

# <square>y</square> <!-- result: 9 -->
# '''

# result = parser.parse(lexer.lex(test))

# for e in result:
#     pprint(e.__dict__)
