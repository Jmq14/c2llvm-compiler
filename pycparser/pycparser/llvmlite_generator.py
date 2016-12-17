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
g_named_argument = {}
g_named_memory = {}

class LLVMGenerator(object):
    def __init__(self):
        pass

    def generate(self, head):
        self.visit(head)
        return g_llvm_module

    # ---------- visit methods ---------

    def visit(self, node, status=0):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node, status)

    def generic_visit(self, node, status=0):
        #~ print('generic:', type(node))
        raise RuntimeError("not implement node: " + node.__class__.__name__)

    def visit_FileAST(self, n, status=0):
        for ext in n.ext:
            self.visit(ext)

    def visit_Decl(self, n, status=0):
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

    def visit_FuncDef(self, n, status=0):
        """
            Generate function.
            n:
                decl -> FuncDecl
                body -> Compound
        """
        global g_named_argument
        global g_named_memory
        global g_llvm_builder

        g_named_argument.clear()
        function = self.visit(n.decl)

        if n.body:
            block = function.append_basic_block(name="entry")
            g_llvm_builder = ir.IRBuilder(block)

            ### Generate body content
            self.visit(n.body)

    def visit_FuncDecl(self, n, status=0):
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

        f = self.get_type(n.type)
        funct_type = ir.FunctionType(f['dtype'], args_type)
        function = ir.Function(g_llvm_module, funct_type, name=f['dname'])

        # Set names for all arguments and add them to the variables symbol table.
        for arg, arg_name in zip(function.args, args_name):
            arg.name = arg_name
            # Add arguments to variable symbol table.
            g_named_argument[arg_name] = arg

        return function

    def visit_ParamList(self, n, status=0):
        args_type = []
        args_name = []
        for arg in n.params:
            a = self.get_type(arg.type)
            args_type.append(a['dtype'])
            args_name.append(a['dname'])

        return args_name, tuple(args_type)

    def visit_Compound(self, n, status=0):
        if n.block_items:
            for stmt in n.block_items:
                self.visit(stmt)

    def visit_Constant(self, n, status=0):
        if n.type == 'int':
            c = ir.Constant(ir.IntType(32), n.value)
        elif n.type == 'float':
            c = ir.Constant(ir.FloatType(), n.value)
        elif n.type == 'double':
            c = ir.Constant(ir.DoubleType(), n.value)
        else:
            raise RuntimeError("not implement constant type: " + n.type)

        return c

    def visit_IdentifierType(self, n, status=0):
        i = n.names
        if i[0] == 'int':
            return ir.IntType(32)
        elif i[0] == 'void':
            return ir.VoidType()
        else:
            raise RuntimeError("not implement type: " + i[0])

    def visit_ID(self, n, status=0):
        """
            Return variable.
            status = 0 -> get pointer
            status = 1 -> get value 
        """
        if n.name in g_named_memory:
            if status == 0:
                return g_named_memory[n.name]
            elif status == 1:
                return g_llvm_builder.load(g_named_memory[n.name])

        elif n.name in g_named_argument:
            return g_named_argument[n.name]
        else:
            raise RuntimeError("Undedined variable: " + n.name)

    def visit_TypeDecl(self, n, status=0):
        """
            Allocate new vadiables.
        """
        ### Allocate and store all the arguments
        typ = self.visit(n.type)
        nam = n.declname

        if nam in g_named_memory or nam in g_named_argument:
            raise RuntimeError("Duplicate variable declaration!")

        g_named_memory[nam] = g_llvm_builder.alloca(typ, name=nam) 

    def visit_Assignment(self, n, status=0):
        if n.op == '=':
            # lvalue -> ans
            # rvalue -> binary op
            ans = self.visit(n.lvalue)
            g_llvm_builder.store(self.visit(n.rvalue), ans)

    def visit_BinaryOp(self, n, status=0):
        if n.op == '+':
            left = self.visit(n.left, 1)
            right = self.visit(n.right, 1)
            return g_llvm_builder.add(left, right)
        else:
            pass

    def visit_Return(self, n, status=0):
        g_llvm_builder.ret(self.visit(n.expr))

    # ---------- custom methods ---------

    def get_type(self, n, status=0):
        """
            type(n) should be TypeDecl
        """
        if type(n) != c_ast.TypeDecl:
            raise RuntimeError("n is not a TypeDecl node!")

        return {'dname': n.declname, 'dtype': self.visit(n.type)}


