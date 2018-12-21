from rply import LexerGenerator

lg = LexerGenerator()


lg.add('LSLASHANGLE', r'</')
lg.add('RSLASHANGLE', r'/>')
lg.add('LANGLE', r'<')
lg.add('RANGLE', r'>')
lg.add('LSQUARE', r'\[')
lg.add('RSQUARE', r'\]')
lg.add('EQUAL', r'=')

lg.add('STRING', r'''(?x)
(r)?
"
[^"]*
"
''')
lg.add('IDENTIFIER', r'[^<>\[\]{}=/\s"]+')

lg.ignore(r'<!--(.|\s)*-->')
lg.ignore(r'\s+')

lexer = lg.build()
