import re

from ply import lex
from ply.lex import TOKEN


class CLexer(object):

    def __init__(self, on_lbrace_func, on_rbrace_func):
        self.on_lbrace_func = on_lbrace_func
        self.on_rbrace_func = on_rbrace_func

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    reserved = {
        'static': 'STATIC',
        'const': 'CONST',
        'int': 'INT',
        'auto': 'AUTO',
    }

    tokens = list(reserved.values()) + ['ID',
                                'LBRACKET','RBRACKET',
                                'LBRACE', 'RBRACE',
                                'INT_CONST_DEC','INT_CONST_OCT',
                                'EQUALS',
                                'COMMA',
                                'SEMI']

    t_EQUALS = r'='

    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_SEMI = r';'

    identifier = r'[a-zA-Z_$][0-9a-zA-Z_$]*'
    integer_suffix_opt = r'(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
    decimal_constant = '(0' + integer_suffix_opt + ')|([1-9][0-9]*' + integer_suffix_opt + ')'
    octal_constant = '0[0-7]*' + integer_suffix_opt


    @TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.reserved.get(t.value, "ID")
        #if t.type == 'ID':
        #    t.type = "TYPEID"
        return t

    @TOKEN(decimal_constant)
    def t_INT_CONST_DEC(self, t):
        return t

    @TOKEN(octal_constant)
    def t_INT_CONST_OCT(self, t):
        return t

    @TOKEN(r'\{')
    def t_LBRACE(self, t):
        self.on_lbrace_func()
        return t
    @TOKEN(r'\}')
    def t_RBRACE(self, t):
        self.on_rbrace_func()
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_comment(self,t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)