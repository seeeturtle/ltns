from collections import namedtuple, OrderedDict

from rply import ParserGenerator

from .lexer import lexer
from .models import (
    LtnsElement,
    LtnsKeyword,
    LtnsSymbol,
    LtnsString,
    LtnsInteger,
    LtnsFloat,
    LtnsComplex,
    LtnsList,
)


pg = ParserGenerator([rule.name for rule in lexer.rules] + ['end$'])

tag = namedtuple('tag', ('name', 'attributes', 'lineno', 'colno'))

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
@pg.production("term : list")
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
    return tag(p[1], p[2], p[0].source_pos.lineno, p[0].source_pos.colno)

@pg.production("start_tag : LANGLE identifier RANGLE")
def start_tag_without_attributes(p):
    return tag(p[1], {}, p[0].source_pos.lineno, p[0].source_pos.colno)

@pg.production("attributes : identifier EQUAL term attributes")
def attributes(p):
    d = OrderedDict([(p[0], p[2])])
    d.update(p[3])

    return d

@pg.production("attributes : identifier EQUAL term")
def attributes_one(p):
    return {p[0]: p[2]}

@pg.production("end_tag : LSLASHANGLE identifier RANGLE")
def end_tag(p):
    return tag(p[1], None, None, None)

@pg.production("empty_tag : LANGLE identifier attributes RSLASHANGLE")
def empty_tag(p):
    return tag(p[1], p[2], p[0].source_pos.lineno, p[0].source_pos.colno)

@pg.production("identifier : IDENTIFIER")
def identifier(p):
    s = p[0].value

    # get base of integer
    prefix_base = {
        '0b': 2,
        '0o': 8,
        '0x': 16,
    }

    base = 10
    for prefix, _base in prefix_base.items():
        if s.startswith(prefix):
            base = _base
    try:
        return LtnsInteger(s, base=base)
    except ValueError:
        pass

    try:
        return LtnsFloat(s)
    except ValueError:
        pass

    try:
        return LtnsComplex(s)
    except ValueError:
        pass

    try:
        if not s.startswith(':'):
            raise ValueError
        s = s[1:]
        return LtnsKeyword(s)
    except ValueError:
        pass

    return LtnsSymbol(s)

@pg.production("string : STRING")
def string(p):
    return LtnsString(p[0].value[1:-1])

@pg.production("list : LSQUARE list_contents RSQUARE")
def list(p):
    return LtnsList(p[1])

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

parser = pg.build()
