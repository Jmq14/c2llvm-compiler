from ply import yacc
import ast
from clex import CLexer

class Coord(object):
    """ Coordinates of a syntactic element. Consists of:
            - File name
            - Line number
            - (optional) column number, for the Lexer
    """
    __slots__ = ('file', 'line', 'column', '__weakref__')
    def __init__(self, file, line, column=None):
        self.file = file
        self.line = line
        self.column = column

    def __str__(self):
        str = "%s:%s" % (self.file, self.line)
        if self.column: str += ":%s" % self.column
        return str


class ParseError(Exception): pass


class CParser(object):
    def __init__(self):
        self.clex = CLexer(
            on_lbrace_func=self._lex_on_lbrace_func,
            on_rbrace_func=self._lex_on_rbrace_func,)
        self.clex.build()
        self.tokens = self.clex.tokens
        self.cparser = yacc.yacc(module=self,
                                 start='translation_unit_or_empty',
                                 debug=True)
        rules_with_opt = [
            'assignment_expression',
            'expression',
            'type_qualifier_list',
        ]
        for rule in rules_with_opt:
            self._create_opt_rule(rule)
        self._scope_stack = [dict()]

    def parse(self, text, filename='', debuglevel=0):
        self.clex.filename = filename
        self.clex.reset_lineno()
        return self.cparser.parse(
            input=text,
            lexer=self.clex,
            debug=debuglevel
        )

    def _create_opt_rule(self, rulename):
        """ Given a rule name, creates an optional ply.yacc rule
            for it. The name of the optional rule is
            <rulename>_opt
        """
        optname = rulename + '_opt'

        def optrule(self, p):
            p[0] = p[1]

        optrule.__doc__ = '%s : empty\n| %s' % (optname, rulename)
        optrule.__name__ = 'p_%s' % optname
        setattr(self.__class__, optrule.__name__, optrule)

    def _coord(self, lineno, column=None):
        return Coord(
                file=self.clex.filename,
                line=lineno,
                column=column)

    def _parse_error(self, msg, coord):
        raise ParseError("%s: %s" % (coord, msg))
    
    def _add_declaration_specifier(self, declspec, newspec, kind):
        """ Declaration specifiers are represented by a dictionary
            with the entries:
            * qual: a list of type qualifiers
            * storage: a list of storage type qualifiers
            * type: a list of type specifiers
            * function: a list of function specifiers

            This method is given a declaration specifier, and a
            new specifier of a given kind.
            Returns the declaration specifier, with the new
            specifier incorporated.
        """
        spec = declspec or dict(qual=[], storage=[], type=[], function=[])
        spec[kind].insert(0, newspec)
        return spec

    def _add_identifier(self, name, coord):
        """ Add a new object, function, or enum member name (ie an ID) to the
            current scope
        """
        if self._scope_stack[-1].get(name, False):
            self._parse_error(
                "Non-typedef %r previously declared as typedef "
                "in this scope" % name, coord)
        self._scope_stack[-1][name] = False

    def _lex_on_lbrace_func(self):
        self._scope_stack.append(dict())

    def _lex_on_rbrace_func(self):
        assert len(self._scope_stack) > 1
        self._scope_stack.pop()

    # To understand what's going on here, read sections A.8.5 and
    # A.8.6 of K&R2 very carefully.
    #
    # A C type consists of a basic type declaration, with a list
    # of modifiers. For example:
    #
    # int *c[5];
    #
    # The basic declaration here is 'int c', and the pointer and
    # the array are the modifiers.
    #
    # Basic declarations are represented by TypeDecl (from module c_ast) and the
    # modifiers are FuncDecl, PtrDecl and ArrayDecl.
    #
    # The standard states that whenever a new modifier is parsed, it should be
    # added to the end of the list of modifiers. For example:
    #
    # K&R2 A.8.6.2: Array Declarators
    #
    # In a declaration T D where D has the form
    #   D1 [constant-expression-opt]
    # and the type of the identifier in the declaration T D1 is
    # "type-modifier T", the type of the
    # identifier of D is "type-modifier array of T"
    #
    # This is what this method does. The declarator it receives
    # can be a list of declarators ending with TypeDecl. It
    # tacks the modifier to the end of this list, just before
    # the TypeDecl.
    #
    # Additionally, the modifier may be a list itself. This is
    # useful for pointers, that can come as a chain from the rule
    # p_pointer. In this case, the whole modifier list is spliced
    # into the new location.
    def _type_modify_decl(self, decl, modifier):
        """ Tacks a type modifier on a declarator, and returns
            the modified declarator.

            Note: the declarator and modifier may be modified
        """
        # ~ print '****'
        # ~ decl.show(offset=3)
        # ~ modifier.show(offset=3)
        # ~ print '****'

        modifier_head = modifier
        modifier_tail = modifier

        # The modifier may be a nested list. Reach its tail.
        #
        while modifier_tail.type:
            modifier_tail = modifier_tail.type

        # If the decl is a basic type, just tack the modifier onto
        # it
        #
        if isinstance(decl, ast.TypeDecl):
            modifier_tail.type = decl
            return modifier
        else:
            # Otherwise, the decl is a list of modifiers. Reach
            # its tail and splice the modifier onto the tail,
            # pointing to the underlying basic type.
            #
            decl_tail = decl

            while not isinstance(decl_tail.type, ast.TypeDecl):
                decl_tail = decl_tail.type

            modifier_tail.type = decl_tail.type
            decl_tail.type = modifier_head
            return decl

    def p_declaration_specifiers_opt(self,p):
        """declaration_specifiers_opt   : empty
                                        | declaration_specifiers
        """
        p[0] = p[1]

    def p_identifier_list_opt(self,p):
        """identifier_list_opt  : empty
                                | identifier_list
        """
        p[0] = p[1]


    def p_init_declarator_list_opt(self,p):
        """init_declarator_list_opt  : empty
                                | init_declarator_list
        """
        p[0] = p[1]


    def p_initializer_list_opt(self,p):
        """initializer_list_opt : empty
                                | initializer_list
        """
        p[0] = p[1]

    def p_assignment_expression_opt(self,p):
        """assignment_expression_opt    : empty
                                        | assignment_expression
        """
        p[0] = p[1]

    def p_type_qualifier_list_opt(self,p):
        """type_qualifier_list_opt  : empty
                                    | type_qualifier_list
        """
        p[0] = p[1]

    def p_assignment_expression(self, p):
        """ assignment_expression   : conditional_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assignment(p[2], p[1], p[3], p[1].coord)
        
    def p_binary_expression(self, p):
        """ binary_expression   : cast_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinaryOp(p[2], p[1], p[3], p[1].coord)

    def p_brace_open(self, p):
        """ brace_open  :   LBRACE
        """
        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

    def p_brace_close(self, p):
        """ brace_close :   RBRACE
        """
        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

    def p_cast_expression_1(self, p):
        """ cast_expression : unary_expression """
        p[0] = p[1]

    def p_conditional_expression(self, p):
        """ conditional_expression  : binary_expression
        """
        if len(p) == 2:
            p[0] = p[1]

    def p_constant_1(self, p):
        """ constant    : INT_CONST_DEC
                        | INT_CONST_OCT
        """
        p[0] = ast.Constant(
            'int', p[1], self._coord(p.lineno(1)))
    
    def p_declaration(self, p):
        """ declaration : decl_body SEMI
        """
        p[0] = p[1]

    def p_declarator_1(self, p):
        """ declarator  : direct_declarator
        """
        p[0] = p[1]

    def p_declaration_specifiers_1(self, p):
        """ declaration_specifiers  : type_qualifier declaration_specifiers_opt
        """
        p[0] = self._add_declaration_specifier(p[2], p[1], 'qual')

    def p_declaration_specifiers_2(self, p):
        """ declaration_specifiers  : type_specifier declaration_specifiers_opt
        """
        p[0] = self._add_declaration_specifier(p[2], p[1], 'type')

    def p_declaration_specifiers_3(self, p):
        """ declaration_specifiers  : storage_class_specifier declaration_specifiers_opt
        """
        p[0] = self._add_declaration_specifier(p[2], p[1], 'storage')
    
    def p_decl_body(self, p):
        """ decl_body : declaration_specifiers init_declarator_list_opt
        """
        spec = p[1]

        # p[2] (init_declarator_list_opt) is either a list or None
        #
        if p[2] is None:
            # By the standard, you must have at least one declarator unless
            # declaring a structure tag, a union tag, or the members of an
            # enumeration.
            #
            ty = spec['type']
            if len(ty) == 1 and isinstance(ty[0], ast.Struct):
                decls = [ast.Decl(
                    name=None,
                    quals=spec['qual'],
                    storage=spec['storage'],
                    funcspec=spec['function'],
                    type=ty[0],
                    init=None,
                    bitsize=None,
                    coord=ty[0].coord)]

        p[0] = decls
        
    def p_direct_declarator_1(self, p):
        """ direct_declarator   : ID
        """
        p[0] = ast.TypeDecl(
            declname=p[1],
            type=None,
            quals=None,
            coord=self._coord(p.lineno(1)))
        
    def p_direct_declarator_3(self, p):
        """ direct_declarator   : direct_declarator LBRACKET type_qualifier_list_opt assignment_expression_opt RBRACKET
        """
        quals = (p[3] if len(p) > 5 else []) or []
        # Accept dimension qualifiers
        # Per C99 6.7.5.3 p7
        arr = ast.ArrayDecl(
            type=None,
            dim=p[4] if len(p) > 5 else p[3],
            dim_quals=quals,
            coord=p[1].coord)

        p[0] = self._type_modify_decl(decl=p[1], modifier=arr)

    def p_empty(self, p):
        'empty : '
        p[0] = None
      
    def p_external_declaration_2(self, p):
        """ external_declaration    : declaration
        """
        p[0] = p[1]

    def p_identifier(self, p):
        """ identifier  : ID """
        p[0] = c_ast.ID(p[1], self._coord(p.lineno(1)))

    def p_identifier_list(self, p):
        """ identifier_list : identifier
                            | identifier_list COMMA identifier
        """
        if len(p) == 2: # single parameter
            p[0] = c_ast.ParamList([p[1]], p[1].coord)
        else:
            p[1].params.append(p[3])
            p[0] = p[1]

    def p_initializer_1(self, p):
        """ initializer : assignment_expression
        """
        p[0] = p[1]

    def p_initializer_2(self, p):
        """ initializer : brace_open initializer_list_opt brace_close
                        | brace_open initializer_list COMMA brace_close
        """
        if p[2] is None:
            p[0] = ast.InitList([], self._coord(p.lineno(1)))
        else:
            p[0] = p[2]
            
    def p_initializer_list(self, p):
        """ initializer_list    : initializer
                                | initializer_list COMMA initializer
        """
        if len(p) == 2: # single initializer
            init = p[1]
            p[0] = ast.InitList([init], p[1].coord)
        else:
            init = p[3]
            p[1].exprs.append(init)
            p[0] = p[1]
            
    def p_init_declarator(self, p):
        """ init_declarator : declarator
                            | declarator EQUALS initializer
        """
        p[0] = dict(decl=p[1], init=(p[3] if len(p) > 2 else None))

    def p_init_declarator_list_1(self, p):
        """ init_declarator_list    : init_declarator
                                    | init_declarator_list COMMA init_declarator
        """
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]
        
    def p_postfix_expression_1(self, p):
        """ postfix_expression  : primary_expression """
        p[0] = p[1]

    def p_primary_expression_2(self, p):
        """ primary_expression  : constant """
        p[0] = p[1]

    def p_storage_class_specifier(self, p):
        """ storage_class_specifier : AUTO
                                    | STATIC
        """
        p[0] = p[1]

    def p_translation_unit_or_empty(self, p):
        """ translation_unit_or_empty   : translation_unit
                                        | empty
        """
        if p[1] is None:
            p[0] = ast.FileAST([])
        else:
            p[0] = ast.FileAST(p[1])

    def p_translation_unit_1(self, p):
        """ translation_unit    : external_declaration
        """
        # Note: external_declaration is already a list
        #
        p[0] = p[1]
        
    def p_type_qualifier(self, p):
        """ type_qualifier  : CONST
        """
        p[0] = p[1]

    def p_type_qualifier_list(self, p):
        """ type_qualifier_list : type_qualifier
                                | type_qualifier_list type_qualifier
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
        
    def p_type_specifier_1(self, p):
        """ type_specifier  : INT
        """
        p[0] = ast.IdentifierType([p[1]], coord=self._coord(p.lineno(1)))

    def p_unary_expression_1(self, p):
        """ unary_expression    : postfix_expression """
        p[0] = p[1]
            



    
