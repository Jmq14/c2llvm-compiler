#------------------------------------------------------------------------------
# llvm_generator.py
#
# LLVM IR generator from pycparser AST nodes based on llvmlite.
# (http://llvmlite.pydata.org/)
#------------------------------------------------------------------------------

from __future__ import print_function
from pycparser import c_ast
from llvmlite import ir

# The LLVM module, which holds all the IR code.
g_llvm_module = ir.Module('my compiler')

# The LLVM instruction builder. Created whenever a new function is entered.
g_llvm_builder = None

# A dictionary that keeps track of which values are defined in the current scope
# and what their LLVM representation is.
g_named_values = {}

class LLVMGenerator(object):
    def __init__(self):
        pass

    def generate(self, head):
        self.visit(head)
        return g_llvm_module

    # ---------- visit methods ---------

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        #~ print('generic:', type(node))
        raise RuntimeError("not implement node: " + node.__class__.__name__)

    def visit_FileAST(self, n):
        for ext in n.ext:
            self.visit(ext)

    def visit_Decl(self, n):
        """
            Declare and allocate the declared variables.
            n:
                type -> FuncDecl | TypeDecl
                init -> expr
        """
        tpy = type(n.type)
        if tpy == c_ast.FuncDecl:
            return self.visit(n.type)
        elif tpy == c_ast.TypeDecl:
            self.visit(n.type)
            # allocate
            if n.init:
                self.visit(n.init)
                # Here we don't handle the default values given 
                # to function arguments

    def visit_FuncDef(self, n):
        """
            Generate function.
            n:
                decl -> FuncDecl
                body -> Compound
        """
        global g_named_values
        global g_llvm_builder
        
        g_named_values.clear()
        function = self.visit(n.decl)

        block = function.append_basic_block(name="entry")
        g_llvm_builder = ir.IRBuilder(block)

        self.visit(n.body)

    def visit_FuncDecl(self, n):
        """
            Return function declaration.
            n:
                args -> paramlist
                type -> TypeDecl
        """
        if n.args:
            args_name, args_type = self.visit(n.args)
        else:
            args_name = []
            args_type = ()

        f = {'dname': n.type.declname, 'dtype': self.visit(n.type.type)}
        funct_type = ir.FunctionType(f['dtype'], args_type)
        function = ir.Function(g_llvm_module, funct_type, name=f['dname'])

        # Set names for all arguments and add them to the variables symbol table.
        for arg, arg_name in zip(function.args, args_name):
            arg.name = arg_name
            # Add arguments to variable symbol table.
            g_named_values[arg_name] = arg

        return function

    def visit_ParamList(self, n):
        args_type = []
        args_name = []
        for arg in n.params:
            a = {'dname': arg.name, 'dtype': self.visit(arg.type.type)}
            args_type.append(a['dtype'])
            args_name.append(a['dname'])

        return args_name, tuple(args_type)

    def visit_Compound(self, n):
        if n.block_items:
            for stmt in n.block_items:
                self.visit(stmt)

    def visit_Constant(self, n):
        if n.type == 'int':
            c = ir.Constant(ir.IntType(32), n.value)
        elif n.type == 'float':
            c = ir.Constant(ir.FloatType(), n.value)
        elif n.type == 'double':
            c = ir.Constant(ir.DoubleType(), n.value)
        else:
            raise RuntimeError("not implement constant type: " + n.type)

        return c

    def visit_IdentifierType(self, n):
        i = n.names
        if i[0] == 'int':
            return ir.IntType(32)
        elif i[0] == 'void':
            return ir.VoidType()
        else:
            raise RuntimeError("not implement type: " + i[0])

    def visit_statement(self, n):
        pass

    def visit_Assignment(self, n):
        pass

    def visit_BinaryOp(self, n):
        pass

    def visit_Return(self, n):
        g_llvm_builder.ret(self.visit(n.expr))

    # ---------- custom generation methods ---------

    def _generate_type(self, n):
        typ = type(n)

        if typ == c_ast.FuncDecl:
            self.visit(n)
        elif typ == c_ast.TypeDecl:
            pass


