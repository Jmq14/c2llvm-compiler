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
g_named_function = {}
g_global_variable = {}

# current function
g_current_function = None

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
            if isinstance(ext, c_ast.FuncDef):
                self.visit(ext)
            if isinstance(ext, c_ast.Decl):
                self.global_visit(ext)

    def visit_Decl(self, n, status=0):
        """
            Declare and allocate the declared variables.
            n:
                type -> FuncDecl | TypeDecl | ArrayDecl
                init -> expr
        """
        tpy = type(n.type)
        if tpy == c_ast.FuncDecl:
            return self.visit(n.type)
        elif tpy in {c_ast.TypeDecl, c_ast.ArrayDecl, c_ast.PtrDecl}:
            d = self.visit(n.type)
            # allocate
            if n.init:
                g_llvm_builder.store(self.visit(n.init), d)
                # Here we don't handle the default values given 
                # to function arguments


    def visit_ArrayDecl(self, n, status=0):
        """
            Allocate new array.
        """
        d = self.get_type(n.type)
        nam = d['dname']
        typ = d['dtype']

        self.declaration_verify(nam)

        g_named_memory[nam] = g_llvm_builder.alloca(ir.ArrayType(typ, int(n.dim.value)), name=nam)
        return g_named_memory[nam]

    def visit_ArrayRef(self, n, status=0):
        """
            Return variable in an array.
            status == 0 -> get pointer
            status == 1 -> get value
        """
        arr = self.visit(n.name)
        index = self.visit(n.subscript)
        zero = ir.Constant(ir.IntType(32), 0)
        ele = g_llvm_builder.gep(arr, [zero, index], inbounds=True)
        if status == 0:
            return ele
        elif status == 1:
            return g_llvm_builder.load(ele)

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
        global g_current_function

        g_named_argument.clear()
        function = self.visit(n.decl)
        g_current_function = function

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

        global g_named_function
        g_named_function[f['dname']] = function

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
            status == 0 -> get pointer
            status ==1 -> get value
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
            Allocate new variables.
        """
        ### Allocate and store all the arguments
        typ = self.visit(n.type)
        nam = n.declname

        self.declaration_verify(nam)

        g_named_memory[nam] = g_llvm_builder.alloca(typ, name=nam)
        return g_named_memory[nam]

    def visit_PtrDecl(self, n, status=0):
        d = self.get_type(n.type)
        nam = d['dname']
        typ = d['dtype']
        ptr = ir.PointerType(typ)
        g_named_memory[nam] = g_llvm_builder.alloca(ptr, name=nam)
        return g_named_memory[nam]

    def visit_Assignment(self, n, status=0):
        if n.op == '=':
            # lvalue -> ans
            # rvalue -> binary op
            ans = self.visit(n.lvalue, 0)
            right = self.visit(n.rvalue, 1)
            g_llvm_builder.store(right, ans)

    def visit_BinaryOp(self, n, status=0):
        left = self.visit(n.left, 1)
        right = self.visit(n.right, 1)
        if n.op == '+':
            return g_llvm_builder.add(left, right)
        elif n.op == '-':
            return g_llvm_builder.sub(left, right)
        elif n.op == '*':
            return g_llvm_builder.mul(left, right)
        elif n.op == '/':
            return g_llvm_builder.sdiv(left, right)
        elif n.op in {'<', '<=', '==', '!=', '>=', '>'}:
            return g_llvm_builder.icmp_signed(n.op, left, right)
        elif n.op == '===':
            return g_llvm_builder.icmp_signed('==', left, right)
        elif n.op == '&&':
            return g_llvm_builder.and_(left, right)
        elif n.op == '||':
            return g_llvm_builder.or_(left, right)
        else:
            raise RuntimeError("not implement binary operator!")

    def visit_UnaryOp(self, n, status=0):
        if (n.op == '&'):
            return self.visit(n.expr, 0)
        pass

    def visit_FuncCall(self, n, status=0):
        func_name = n.name.name
        if func_name not in g_named_function:
            raise RuntimeError("Undefined function: " + func_name)
        function = g_named_function[func_name]
        return g_llvm_builder.call(function, self.visit(n.args))

    def visit_ExprList(self, n, status=0):
        """
            Return a list of FuncCall arguments
        """
        arg_list = []
        for arg in n.exprs:
            arg_list.append(self.visit(arg))
        return arg_list

    def visit_If(self, n, status=0):
        if n.iffalse:
            with g_llvm_builder.if_else(self.visit(n.cond)) as (then, otherwise):
                with then:
                    self.visit(n.iftrue)
                with otherwise:
                    self.visit(n.iffalse)
        else:
            with g_llvm_builder.if_then(self.visit(n.cond)):
                self.visit(n.iftrue)

    def visit_While(self, n, status=0):
        while_cmp = g_current_function.append_basic_block()
        while_entry = g_current_function.append_basic_block()
        while_end = g_current_function.append_basic_block()

        g_llvm_builder.position_at_end(while_cmp)
        c = self.visit(n.cond)
        g_llvm_builder.cbranch(c, while_entry, while_end)

        g_llvm_builder.position_at_end(while_entry)
        self.visit(n.stmt)
        g_llvm_builder.branch(while_cmp)

        g_llvm_builder.position_at_end(while_end)

    def visit_Return(self, n, status=0):
        g_llvm_builder.ret(self.visit(n.expr))


    # ---------- global variable declaration --------

    def global_visit(self, node, status=0):
        method = 'global_visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node, status)

    def global_visit_Decl(self, n, status=0):
        g = self.global_visit(n.type)
        # allocate
        if n.init:
            g.initializer = self.global_visit(n.init, n.name)
        pass

    def global_visit_ArrayDecl(self, n, status=0):
        d = self.get_type(n.type)
        nam = d['dname']
        typ = d['dtype']
        g_global_variable[nam] = \
            ir.GlobalVariable(g_llvm_module, ir.ArrayType(typ, int(n.dim.value)), name=nam)
        return g_global_variable[nam]

    def global_visit_TypeDecl(self, n, status=0):
        typ = self.visit(n.type)
        nam = n.declname
        g_global_variable[nam] = \
            ir.GlobalVariable(g_llvm_module, typ, name=nam)
        return g_global_variable[nam]

    def global_visit_InitList(self, n, status=0):
        # arr = ir.Constant(ir.ArrayType(typ, int(len(n.exprs)))
        return ir.Constant.literal_array([self.visit(ele) for ele in n.exprs])

    def global_visit_Constant(self, n, status=0):
        return self.visit(n)

    # ---------- custom methods ---------

    def get_type(self, n, status=0):
        """
            type(n) should be TypeDecl
        """
        if type(n) != c_ast.TypeDecl:
            raise RuntimeError("n is not a TypeDecl node!")

        return {'dname': n.declname, 'dtype': self.visit(n.type)}

    def extern_function(self, n):
        pass

    # ---------- check & handle error ----------

    def declaration_verify(self, name):
        if name in g_named_memory.keys() \
                or name in g_named_argument.keys() \
                or name in g_global_variable.keys():
            raise RuntimeError("Duplicate variable declaration!")

    def reference_verify(self, name, type):
        pass

