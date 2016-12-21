#------------------------------------------------------------------------------
# llvm_generator.py
#
# LLVM IR generator from pycparser AST nodes based on llvmlite.
# (http://llvmlite.pydata.org/)
#------------------------------------------------------------------------------

from __future__ import print_function
from llvmlite import ir
import ast

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
g_type_define = {}

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
            if isinstance(ext, ast.FuncDef):
                self.visit(ext, status=0)
            elif isinstance(ext, ast.Decl):
                self.visit(ext, status=1)

    def visit_Decl(self, n, status=0):
        """
            Declare and allocate the declared variables.
            n:
                type -> FuncDecl | ArrayDecl | PrtDecl | Struct | IndentifyType
                init -> expr
            status == 0: local
            status == 1: global
            status == 2: return element type
        """
        # tpy = type(n.type)
        # if tpy == ast.FuncDecl:
        #     return self.visit(n.type)
        # elif tpy in {ast.TypeDecl, ast.ArrayDecl, ast.PtrDecl}:
        #     d = self.get_decl(n)
        #     nam = d['dname']
        #     typ = d['dtype']
        #     g_named_memory[nam] = g_llvm_builder.alloca(typ, name=nam)
        #     # allocate
        #     if n.init:
        #         g_llvm_builder.store(self.visit(n.init, 1), g_named_memory[nam])
                # Here we don't handle the default values given 
                # to function arguments
        d = self.generate_declaration(n.type, status, [])
        if n.init:
            if status == 0:
                g_llvm_builder.store(self.visit(n.init, 1), g_named_memory[n.name])
            elif status == 1:
                g_global_variable[n.name].initializer = self.visit(n.init, n.name)

        if status == 2:
            return d

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
        index = self.visit(n.subscript, 1)
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
        function = self.visit(n.decl, status=2)
        g_current_function = function

        if n.body:
            block = function.append_basic_block(name="entry")
            g_llvm_builder = ir.IRBuilder(block)

            ### Allocate all arguments
            for arg in function.args:
                nam = arg.name
                g_named_memory[nam] = g_llvm_builder.alloca(arg.type.pointee, name=nam)

            ### Generate body content
            self.visit(n.body)
        else:
            g_current_function = None
            function.is_declaration = True

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
            a = self.get_decl(arg)
            args_type.append(a['dtype'])
            args_name.append(a['dname'])

        return args_name, tuple(args_type)

    def visit_Compound(self, n, status=0):
        if n.block_items:
            for stmt in n.block_items:
                self.visit(stmt, status=0)

    def visit_Constant(self, n, status=0):
        if n.type == 'int':
            c = ir.Constant(ir.IntType(32), n.value)
        elif n.type == 'float':
            c = ir.Constant(ir.FloatType(), n.value)
        elif n.type == 'double':
            c = ir.Constant(ir.DoubleType(), n.value)
        elif n.type == 'string':
            typ = ir.ArrayType(ir.IntType(8), len(n.value))
            # TODO: prevent duplicate global name!
            tmp = ir.GlobalVariable(g_llvm_module, typ, name='.str')
            tmp.initializer = ir.Constant(typ, bytearray(n.value))
            tmp.global_constant = True

            g_global_variable['.str'] = tmp
            zero = ir.Constant(ir.IntType(32), 0)
            return g_llvm_builder.gep(tmp, [zero, zero], inbounds=True)
        else:
            raise RuntimeError("not implement constant type: " + n.type)
        return c

    def visit_IdentifierType(self, n, status=0):
        if n.spec:
            # Decl type
            name = n.spec
            if name == 'int':
                return ir.IntType(32);
            if name == 'char':
                return ir.IntType(8);
            elif name == 'void':
                return ir.VoidType()
            elif name in g_type_define:
                context = g_llvm_module.context
                st = context.get_identified_type(n.name)
                return st
            else:
                raise RuntimeError("not implement type: " + name)
        else:
            # variable ID
            if n.name in g_named_memory:
                if status == 0:
                    return g_named_memory[n.name]
                elif status == 1:
                    return g_llvm_builder.load(g_named_memory[n.name])

            elif n.name in g_global_variable:
                if status == 0:
                    return g_global_variable[n.name]
                elif status == 1:
                    return g_global_variable[n.name]
            # elif n.name in g_named_argument:
            #     return g_named_argument[n.name]
            else:
                raise RuntimeError("Undedined variable: " + n.name)

    def visit_ID(self, n, status=0):
        """
            Return variable.
            status == 0 -> get pointer
            status ==1 -> get value
        """
        if n.name == 'NULL' or n.name == 'null':
            return 'NULL'
        if n.name in g_named_memory:
            if status == 0:
                return g_named_memory[n.name]
            elif status == 1:
                return g_llvm_builder.load(g_named_memory[n.name])
        elif n.name in g_global_variable:
            if status == 0:
                return g_global_variable[n.name]
            elif status == 1:
                return g_global_variable[n.name]
        # elif n.name in g_named_argument:
        #     return g_named_argument[n.name]
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
            if right == 'NULL':
                right = ir.Constant(ir.IntType(32), 0).bitcast(ans.type)
            g_llvm_builder.store(right, ans)

    def visit_BinaryOp(self, n, status=0):
        left = self.visit(n.left, 1)
        right = self.visit(n.right, 1)
        if right == 'NULL':
            right = ir.Constant(ir.IntType(32), 0).bitcast(left.type)
        if left == 'NULL':
            left = ir.Constant(ir.IntType(32), 0).bitcast(right.type)
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
            function, args = self.extern_function(n)
        else:
            function = g_named_function[func_name]
            args = [] if n.args is None else self.visit(n.args)
        return g_llvm_builder.call(function, args)

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
        g_llvm_builder.branch(while_cmp)

        g_llvm_builder.position_at_end(while_cmp)
        c = self.visit(n.cond)
        g_llvm_builder.cbranch(c, while_entry, while_end)

        g_llvm_builder.position_at_end(while_entry)
        self.visit(n.stmt)
        g_llvm_builder.branch(while_cmp)

        g_llvm_builder.position_at_end(while_end)

    def visit_Return(self, n, status=0):
        g_llvm_builder.ret(self.visit(n.expr))

    def visit_Struct(self, n, status=0):
        context = g_llvm_module.context
        st = context.get_identified_type(n.name)
        return st

    def visit_StructRef(self, n, status=0):
        if n.type == '->':
            s = self.visit(n.name)

            context = g_llvm_module.context
            st_name = s.type.pointee.name
            st_field = n.field.name
            st = context.get_identified_type(st_name)
            if st_field not in g_type_define[st_name]:
                raise RuntimeError("Field not defined: " + st_field)

            zero = ir.Constant(ir.IntType(32), 0)
            index = ir.Constant(ir.IntType(32), g_type_define[st_name].index(st_field))
            ele = g_llvm_builder.gep(s, [zero, index], inbounds=True)
        return ele

    def visit_InitList(self, n, status=0):
        # arr = ir.Constant(ir.ArrayType(typ, int(len(n.exprs)))
        return ir.Constant.literal_array([self.visit(ele) for ele in n.exprs])

    # ---------- global variable declaration --------

    def global_visit(self, node, status=0):
        method = 'global_visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node, status)

    def global_visit_Decl(self, n, status=0):
        d = self.get_decl(n)
        nam = d['dname']
        typ = d['dtype']
        g_global_variable[nam] = \
            ir.GlobalVariable(g_llvm_module, typ, name=nam)
        # allocate
        if n.init:
            g_global_variable[nam].initializer = self.global_visit(n.init, n.name)
        pass

    def global_visit_ArrayDecl(self, n, status=0):
        d = self.get_type(n.type)
        nam = d['dname']
        typ = d['dtype']
        g_global_variable[nam] = \
            ir.GlobalVariable(g_llvm_module, ir.ArrayType(typ, int(n.dim.value)), name=nam)
        return g_global_variable[nam]

    def global_visit_TypeDecl(self, n, status=0):
        if isinstance(n.type, ast.Struct):
            typ = self.global_visit(n.type)
            if n.declname:
                nam = n.declname
                g_global_variable[nam] = \
                    ir.GlobalVariable(g_llvm_module, typ, name=nam)
                return g_global_variable[nam]
            return None
        else:
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

    def global_visit_Struct(self, n, status=0):
        context = g_llvm_module.context
        st = context.get_identified_type(n.name)
        elements = [self.get_decl(it) for it in n.decls]
        types = [ele['dtype'] for ele in elements]
        g_type_define[n.name] = [ele['dname'] for ele in elements]
        st.set_body(*types)
        return st

    # ---------- custom methods ---------

    def get_decl(self, n):
        """
            type(n) should be Decl or subclass of Decl
        """
        if isinstance(n, ast.PtrDecl):
            return ir.PointerType(self.get_decl(n.type))
        if isinstance(n, ast.ArrayDecl):
            return ir.ArrayType(self.get_decl(n.type), int(n.dim.value))
        if isinstance(n, ast.TypeDecl):
            return self.visit(n.type)
        if isinstance(n, ast.Decl):
            return {'dname': n.name, 'dtype': self.get_decl(n.type)}

    def get_type(self, n):
        """
            type(n) should be TypeDecl
        """
        if type(n) != ast.TypeDecl:
            raise RuntimeError("n is not a TypeDecl node!")

        return {'dname': n.declname, 'dtype': self.visit(n.type)}

    def extern_function(self, n):
        if n.name.name == 'printf':
            func_type = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
            args = []
            for index, arg in enumerate(n.args.exprs):
                if index == 0:
                    args.append(self.visit(arg))
                else:
                    args.append(self.visit(arg.expr, status=1))

            return g_llvm_module.declare_intrinsic(n.name.name, (), func_type), args

    def get_element(self, n, arg=None):
        if arg:
            typ = type(n)
            if typ == ast.PtrDecl:
                return ir.PointerType(arg)
            elif typ == ast.ArrayDecl:
                return ir.ArrayType(arg, int(n.dim.value))
            elif typ == ast.FuncDecl:
                if n.args:
                    paramtypes = [self.generate_declaration(param, status=2) for param in n.args]
                else:
                    paramtypes = []
                return ir.FunctionType(arg, paramtypes)
            else:
                return None
        else:
            if n == 'int':
                return ir.IntType(32);
            elif n == 'char':
                return ir.IntType(8);
            elif n == 'void':
                return ir.VoidType()
            elif n in g_type_define:
                context = g_llvm_module.context
                return context.get_identified_type(n.name)
            else:
                return None

    def generate_declaration(self, n, status=0, motifiers=[]):
        """
            status == 0: allocate local
            status == 1: allocate global
            status == 2: return element type
        """
        typ = type(n)

        if typ == ast.IdentifierType:
            # return a variable declaration

            current = self.get_element(n.spec[0], None)
            for m in motifiers:
                current = self.get_element(m, current)

            if status == 0:
                global g_named_memory
                g_named_memory[n.name] = g_llvm_builder.alloca(current, name=n.name)
            elif status == 1:
                global g_global_variable
                g_global_variable[n.name] = \
                    ir.GlobalVariable(g_llvm_module, current, name=n.name)
            elif status == 2:
                if len(motifiers) > 0 and type(motifiers[0]) == ast.FuncDecl:
                    function = ir.Function(g_llvm_module, current, name=n.name)
                    if motifiers[0].args:
                        paranames = [param.name for param in motifiers[0].args]
                        for arg, arg_name in zip(function.args, paranames):
                            arg.name = arg_name
                            # Add arguments to variable symbol table.
                            g_named_argument[arg_name] = arg
                    return function
                else:
                    return current

        elif typ == ast.Struct:
            # return a type
            context = g_llvm_module.context
            st = context.get_identified_type(n.name)
            global g_type_define
            if status == 0:
                return st
            elif status == 1 and n.name not in g_type_define:
                g_type_define[n.name] = [ele.name for ele in n.decls]
                types = [self.generate_declaration(ele.type, status=2) for ele in n.decls]
                st.set_body(*types)
            else:
                if len(motifiers) > 0 and type(motifiers[0]) == ast.FuncDecl:
                    function = ir.Function(g_llvm_module, st, name=n.name)
                    paranames = [param.name for param in motifiers[0].args]
                    for arg, arg_name in zip(function.args, paranames):
                        arg.name = arg_name
                        # Add arguments to variable symbol table.
                        g_named_argument[arg_name] = arg
                    return function
                else:
                    return st

        elif typ in {ast.ArrayDecl, ast.FuncDecl, ast.PtrDecl}:
            return self.generate_declaration(n.type, status, motifiers+[n])


    # ---------- check & handle error ----------

    def declaration_verify(self, name):
        if name in g_named_memory.keys() \
                or name in g_named_argument.keys() \
                or name in g_global_variable.keys():
            raise RuntimeError("Duplicate variable declaration!")

    def reference_verify(self, name, type):
        pass

