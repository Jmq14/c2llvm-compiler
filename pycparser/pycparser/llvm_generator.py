#------------------------------------------------------------------------------
# llvm_generator.py
#
# LLVM IR generator from pycparser AST nodes.
#------------------------------------------------------------------------------

from __future__ import print_function
from . import c_ast
from llvm.core import Module, Constant, Type, Function, Builder, FCMP_ULT

# The LLVM module, which holds all the IR code.
g_llvm_module = Module.new('my jit')

# The LLVM instruction builder. Created whenever a new function is entered.
g_llvm_builder = None

# A dictionary that keeps track of which values are defined in the current scope
# and what their LLVM representation is.
g_named_values = {}

# function declaration
g_function = None


class LLVMGenerator(object):
    """ Uses the same visitor pattern as c_ast.NodeVisitor, but modified to
        return a value from each visit method, using string accumulation in
        generic_visit.
    """
    def __init__(self):
        pass

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        #~ print('generic:', type(node))
        if node is None:
            return ''
        else:
            return ''.join(self.visit(c) for c_name, c in node.children())

    def visit_Constant(self, n):
        typ = self._generate_llvm_type([n.type])
        if n.type == 'int':
            c = Constant.int(typ, n.value)
        elif n.type == 'float':
            c = Constant.real(typ, n.value)
        return c

    def visit_IdentifierType(self, n):
        return self._generate_type(n)

    def visit_Decl(self, n, no_type=False):
        # no_type is used when a Decl is part of a DeclList, where the type is
        # explicitly only for the first declaration in a list.
        #
        s = n.name if no_type else self._generate_decl(n)
        if n.bitsize: s += ' : ' + self.visit(n.bitsize)
        if n.init:
            s += ' = ' + self._visit_expr(n.init)
        return s

    def visit_FuncDef(self, n):
        g_named_values.clear()
        function = self.visit(n.decl)

        block = function.append_basic_block('entry')

        global g_llvm_builder
        g_llvm_builder = Builder.new(block)

        self.indent_level = 0
        # Finish off the function.

        try:
            s = self.visit(n.body)
            # Validate the generated code, checking for consistency.
            function.verify()
        except:
            function.delete()
            raise
        return function

    def visit_FileAST(self, n):
        s = ''
        for ext in n.ext:
            if isinstance(ext, c_ast.FuncDef):
                s = self.visit(ext)
            elif isinstance(ext, c_ast.Pragma):
                s = self.visit(ext) + '\n'
            else:
                s = self.visit(ext) + ';\n'
            ## TODO: how to concat?
        return s

    def visit_Compound(self, n):
        if n.block_items:
            for stmt in n.block_items:
                return self.visit(stmt)
                # TODO: how to concat??

    def visit_EmptyStatement(self, n):
        pass

    def visit_ParamList(self, n):
        pass

    def visit_Return(self, n):
        #global g_llvm_builder
        return g_llvm_builder.ret(self.visit(n.expr))

    def visit_FuncDecl(self, n):
        return self._generate_func(n)
        #return self._generate_type(n)


    def _generate_stmt(self, n, add_indent=False):
        """ Generation from a statement node. This method exists as a wrapper
            for individual visit_* methods to handle different treatment of
            some statements in this context.
        """
        return self.visit(n)

    def _generate_func(self, n):
        args_type = []
        args_name = []
        for arg in n.args.params:
            a = self.visit(arg)
            args_type.append(a['dtype'])
            args_name.append(a['dname'])

        f = self._generate_decl(n)
        funct_type = Type.function(f['dtype'], args_type, False)

        function = Function.new(
            g_llvm_module, funct_type, f['dname'])


        # Set names for all arguments and add them to the variables symbol table.
        for arg, arg_name in zip(function.args, args_name):
            arg.name = arg_name
            # Add arguments to variable symbol table.
            g_named_values[arg_name] = arg

        return function

    def _generate_decl(self, n):
        """ Generation from a Decl node.
        """
        return self._generate_type(n.type)

    def _generate_llvm_type(self, id):
        if id[0] == 'int':
            return Type.int()
        elif id[0] == 'void':
            return Type.void()
        else:
            return None

    def _generate_type(self, n, modifiers=[]):
        """ Recursive generation from a type node. n is the type node.
            modifiers collects the PtrDecl, ArrayDecl and FuncDecl modifiers
            encountered on the way down to a TypeDecl, to allow proper
            generation from it.
        """
        typ = type(n)
        #~ print(n, modifiers)

        if typ == c_ast.TypeDecl:
            a = {'dname': n.declname, 'dtype': self.visit(n.type)}
            return a

        elif typ == c_ast.Decl:
            return self._generate_decl(n.type)

        elif typ == c_ast.Typename:
            return self._generate_type(n.type)

        elif typ == c_ast.IdentifierType:
            return self._generate_llvm_type(n.names)
            
        elif typ == c_ast.FuncDecl:
            return self._generate_func(n)

        elif typ in (c_ast.ArrayDecl, c_ast.PtrDecl):
            return self._generate_type(n.type, modifiers + [n])
        else:
            return self.visit(n)
