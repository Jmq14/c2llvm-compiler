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
        'char': 'CHAR',
        'case': 'CASE',
        'switch': 'SWITCH',
        'break': 'BREAK',
        'return': 'RETURN',
        'continue': 'CONTINUE',
        'default': 'DEFAULT',
        'if': 'IF',
        'else': 'ELSE',
        'auto': 'AUTO',
    }

    tokens = list(reserved.values()) + ['ID',
                                        'LBRACKET', 'RBRACKET',
                                        'LBRACE', 'RBRACE',
                                        'LPAREN', 'RPAREN',
                                        'INT_CONST_DEC', 'INT_CONST_OCT', 'CHAR_CONST',
                                        'EQUALS',
                                        'MINUS',
                                        'COMMA', 'SEMI', 'COLON',
                                        ]

    t_EQUALS = r'='
    t_MINUS = r'-'

    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','
    t_SEMI = r';'
    t_COLON = r':'

    identifier = r'[a-zA-Z_$][0-9a-zA-Z_$]*'
    integer_suffix_opt = r'(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
    decimal_constant = '(0' + integer_suffix_opt + ')|([1-9][0-9]*' + integer_suffix_opt + ')'
    octal_constant = '0[0-7]*' + integer_suffix_opt

    simple_escape = r"""([a-zA-Z._~!=&\^\-\\?'"])"""
    decimal_escape = r"""(\d+)"""
    hex_escape = r"""(x[0-9a-fA-F]+)"""

    escape_sequence = r"""(\\(""" + simple_escape + '|' + decimal_escape + '|' + hex_escape + '))'
    cconst_char = r"""([^'\\\n]|""" + escape_sequence + ')'
    char_const = "'" + cconst_char + "'"

    @TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.reserved.get(t.value, "ID")
        # if t.type == 'ID':
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

    # Must come before bad_char_const, to prevent it from
    # catching valid char constants as invalid
    #
    @TOKEN(char_const)
    def t_CHAR_CONST(self, t):
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_comment(self, t):
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
