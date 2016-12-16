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

    def visit_ASTFile(self, n):
        pass

    def visit_Decl(self, n):
        pass

    def visit_FuncDef(self, n):
        pass

    def visit_FuncDecl(self, n):
        pass

    def visit_ParamList(self, n):
        pass

    def visit_Compound(self, n):
        pass

    def visit_Constant(self, n):
        pass

    def visit_IdentifierType(self, n):
        pass

    def visit_statement(self, n):
        pass

    def visit_Assignment(self, n):
        pass

    def visit_BinaryOp(self, n):
        pass

    def visit_Return(self, n):
        pass

    # ---------- custom generation methods ---------

    def generate_something(self, n):
        pass
