import ast

from ltns.compiler import ltns_compile, ltns_parse

code = ltns_compile(ltns_parse('''
<if>
  True
  <do>
    <print end="">"This is: "</print>
    <print>"True!"</print>
  </do>
  <do>
    <print end="">"This is: "</print>
    <print>"False!"</print>
  </do>
</if>
'''))

exec(code)
