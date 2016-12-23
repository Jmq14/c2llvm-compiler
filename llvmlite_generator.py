#-*- encoding: utf-8 -*-
#------------------------------------------------------------------------------
# llvm_generator.py
#
# LLVM IR generator from pycparser AST nodes based on llvmlite.
# (http://llvmlite.pydata.org/)
#------------------------------------------------------------------------------

from __future__ import print_function
from llvmlite import ir
from llvmlite import binding
import ast

class LLVMGenerator(object):
    def __init__(self):
        # The LLVM module, which holds all the IR code.
        self.g_llvm_module = ir.Module('my compiler')

        # The LLVM instruction builder. Created whenever a new function is entered.
        self.g_llvm_builder = None

        # A dictionary that keeps track of which values are defined in the current scope
        # and what their LLVM representation is.
        self.g_named_argument = {}
        self.g_named_memory = {}
        self.g_named_function = {}
        self.g_global_variable = {}
        self.g_type_define = {}

        # current function
        self.g_current_function = None
        # stack blocks
        self.g_loop_block_start_stack = []
        self.g_loop_block_end_stack = []

        binding.initialize()
        binding.initialize_native_target()

    def generate(self, head):
        self.visit(head)
        return self.g_llvm_module

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
        #     self.g_named_memory[nam] = self.g_llvn_builder.alloca(typ, name=nam)
        #     # allocate
        #     if n.init:
        #         self.g_llvn_builder.store(self.visit(n.init, 1), self.g_named_memory[nam])
                # Here we don't handle the default values given 
                # to function arguments
        d = self.generate_declaration(n, status, [])
        if n.init:
            if status == 0:
                self.g_llvm_builder.store(self.visit(n.init, 1), self.g_named_memory[n.name])
                # ptr = self.g_named_memory[n.name]
                # val_ptr = self.visit(n.init, 1)
                # # [type]* = [arr address]
                # if isinstance(val_ptr.type.pointee, ir.ArrayType):
                #     zero = ir.Constant(ir.IntType(32), 0)
                #     val = self.g_llvm_builder.gep(val_ptr, [zero, zero], inbounds=True)
                #     self.g_llvm_builder.store(val, ptr)
                # else:
                #     self.g_llvm_builder.store(self.g_llvm_builder.load(val_ptr), ptr)
            elif status == 1:
                self.g_global_variable[n.name].initializer = self.visit(n.init, n.name)
        else:
            if status == 1:
                self.g_global_variable[n.name].linkage = "common"
                self.g_global_variable[n.name].align = 4
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

        self.g_named_memory[nam] = self.g_llvm_builder.alloca(ir.ArrayType(typ, int(n.dim.value)), name=nam)
        return self.g_named_memory[nam]

    def visit_ArrayRef(self, n, status=0):
        """
            Return variable in an array.
            status == 0 -> get pointer
            status == 1 -> get value
        """
        arr = self.visit(n.name)
        index = self.visit(n.subscript, 1)
        zero = ir.Constant(ir.IntType(32), 0)
        ele = self.g_llvm_builder.gep(arr, [zero, index], inbounds=True)
        if status == 0:
            return ele
        elif status == 1:
            return self.g_llvm_builder.load(ele)

    def visit_FuncDef(self, n, status=0):
        """
            Generate function.
            n:
                decl -> FuncDecl
                body -> Compound
        """
        self.g_named_argument.clear()
        function = self.visit(n.decl, status=2)
        self.g_current_function = function

        if n.body:
            block = function.append_basic_block(name="entry")
            self.g_llvm_builder = ir.IRBuilder(block)

            ### Allocate  & store all arguments
            for arg in function.args:
                nam = arg.name
                self.g_named_memory[nam] = self.g_llvm_builder.alloca(arg.type, name=nam)
                self.g_llvm_builder.store(arg, self.g_named_memory[nam])

            ### Generate body content
            self.visit(n.body)
        else:
            self.g_current_function = None
            function.is_declaration = True

        self.g_named_memory.clear()
        self.g_named_argument.clear()
        del self.g_loop_block_start_stack[:]
        del self.g_loop_block_end_stack[:]
        self.g_current_function = None

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
        function = ir.Function(self.g_llvm_module, funct_type, name=f['dname'])

        # Set names for all arguments and add them to the variables symbol table.
        for arg, arg_name in zip(function.args, args_name):
            arg.name = arg_name
            # Add arguments to variable symbol table.
            self.g_named_argument[arg_name] = arg
            # Set signed extension for char
            if isinstance(arg.type, ir.IntType):
                arg.set_attributes('signext')

        self.g_named_function[f['dname']] = function

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
        elif n.type == 'char':
            c = ir.Constant(ir.IntType(8), self.char2int(n.value))
        elif n.type == 'string':
            string = self.remove_quotes(n.value)
            string = string.replace('\\n', '\n')
            string += '\0'
            typ = ir.ArrayType(ir.IntType(8), len(string))
            name = '.str' + str(len(self.g_global_variable))
            tmp = ir.GlobalVariable(self.g_llvm_module, typ, name=name)
            tmp.initializer = ir.Constant(typ, bytearray(string))
            tmp.global_constant = True

            self.g_global_variable[name] = tmp
            zero = ir.Constant(ir.IntType(32), 0)
            return self.g_llvm_builder.gep(tmp, [zero, zero], inbounds=True)
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
            elif name in self.g_type_define:
                context = self.g_llvm_module.context
                st = context.get_identified_type(n.name)
                return st
            else:
                raise RuntimeError("not implement type: " + name)
        else:
            # variable ID
            if n.name in self.g_named_memory:
                if status == 0:
                    return self.g_named_memory[n.name]
                elif status == 1:
                    return self.g_llvm_builder.load(self.g_named_memory[n.name])

            elif n.name in self.g_global_variable:
                if status == 0:
                    return self.g_global_variable[n.name]
                elif status == 1:
                    return self.g_global_variable[n.name]
            # elif n.name in self.g_named_argument:
            #     return self.g_named_argument[n.name]
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
        if n.name in self.g_named_memory:
            if status == 0:
                return self.g_named_memory[n.name]
            elif status == 1:
                return self.g_llvm_builder.load(self.g_named_memory[n.name])
        elif n.name in self.g_global_variable:
            if status == 0:
                return self.g_global_variable[n.name]
            elif status == 1:
                return self.g_global_variable[n.name]
        # elif n.name in self.g_named_argument:
        #     return self.g_named_argument[n.name]
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

        self.g_named_memory[nam] = self.g_llvm_builder.alloca(typ, name=nam)
        return self.g_named_memory[nam]

    def visit_PtrDecl(self, n, status=0):
        d = self.get_type(n.type)
        nam = d['dname']
        typ = d['dtype']
        ptr = ir.PointerType(typ)
        self.g_named_memory[nam] = self.g_llvm_builder.alloca(ptr, name=nam)
        return self.g_named_memory[nam]

    def visit_Assignment(self, n, status=0):
        if n.op == '=':
            # lvalue -> ans
            # rvalue -> binary op
            ans = self.visit(n.lvalue, 0)
            right = self.visit(n.rvalue, 1)
            if right == 'NULL':
                right = ir.Constant(ir.IntType(32), 0).bitcast(ans.type)
            self.g_llvm_builder.store(right, ans)

    def visit_BinaryOp(self, n, status=1):
        left = self.visit(n.left, status)
        right = self.visit(n.right, 1)
        if right == 'NULL':
            right = ir.Constant(ir.IntType(32), 0).bitcast(left.type)
        if left == 'NULL':
            left = ir.Constant(ir.IntType(32), 0).bitcast(right.type)
        if n.op == '+':
            # ptr + int: get the address
            if isinstance(left.type, ir.PointerType):
                if isinstance(left.type.pointee, ir.ArrayType):
                    zero = ir.Constant(ir.IntType(32), 0)
                    first_addr = self.g_llvm_builder.gep(left, [zero, zero], inbounds=True)
                    return self.g_llvm_builder.gep(first_addr, [right], inbounds=True)
                elif isinstance(left.type.pointee, ir.IntType):
                    pass

            return self.g_llvm_builder.add(left, right)
        elif n.op == '-':
            return self.g_llvm_builder.sub(left, right)
        elif n.op == '*':
            return self.g_llvm_builder.mul(left, right)
        elif n.op == '/':
            return self.g_llvm_builder.sdiv(left, right)
        elif n.op in {'<', '<=', '==', '!=', '>=', '>'}:
            return self.g_llvm_builder.icmp_signed(n.op, left, right)
        elif n.op == '===':
            return self.g_llvm_builder.icmp_signed('==', left, right)
        elif n.op == '&&':
            left = self.g_llvm_builder.icmp_signed('!=', left, ir.Constant(left.type, 0))
            right = self.g_llvm_builder.icmp_signed('!=', right, ir.Constant(right.type, 0))
            return self.g_llvm_builder.and_(left, right)
        elif n.op == '||':
            left = self.g_llvm_builder.icmp_signed('!=', left, ir.Constant(left.type, 0))
            right = self.g_llvm_builder.icmp_signed('!=', right, ir.Constant(right.type, 0))
            return self.g_llvm_builder.or_(left, right)
        else:
            raise RuntimeError("not implement binary operator!")

    def visit_UnaryOp(self, n, status=0):
        if (n.op == '&'):
            return self.visit(n.expr, 0)
        elif (n.op == '!'):
            obj = self.visit(n.expr, 1)
            return self.g_llvm_builder.icmp_signed('==', obj, ir.Constant(obj.type, 0))
        elif (n.op == '*'):
            return self.visit(n.expr, 1)
        elif (n.op == '-'):
            return self.g_llvm_builder.neg(self.visit(n.expr, 1))

    def visit_FuncCall(self, n, status=0):
        func_name = n.name.name
        if func_name not in self.g_named_function:
            function, args = self.extern_function(n)
        else:
            function = self.g_named_function[func_name]
            args = [] if n.args is None else self.visit(n.args, 1)
            for i, (param, arg) in enumerate(zip(args, function.args)):
                if isinstance(arg.type, ir.IntType) and isinstance(param.type, ir.IntType):
                    if arg.type.width > param.type.width:
                        args[i] = self.g_llvm_builder.sext(param, arg.type)
                    elif arg.type.width < param.type.width:
                        args[i] = self.g_llvm_builder.trunc(param, arg.type)
        return self.g_llvm_builder.call(function, args)

    def visit_ExprList(self, n, status=0):
        """
            Return a list of FuncCall arguments
        """
        arg_list = []
        for arg in n.exprs:
            arg_list.append(self.visit(arg, status))
        return arg_list

    def visit_If(self, n, status=0):
        cond = self.visit(n.cond, 1)
        if type(cond) is not ir.IntType(1):
            cond = self.g_llvm_builder.icmp_signed('!=', cond, ir.Constant(cond.type, 0))
        if n.iffalse:
            with self.g_llvm_builder.if_else(cond) as (then, otherwise):
                with then:
                    self.visit(n.iftrue)
                with otherwise:
                    self.visit(n.iffalse)
        else:
            with self.g_llvm_builder.if_then(cond):
                self.visit(n.iftrue)
        # if n.iffalse:
        #     iftrue = self.g_current_function.append_basic_block()
        #     iffalse = self.g_current_function.append_basic_block()
        #     ifend = self.g_current_function.append_basic_block()
        #
        #     self.g_llvm_builder.cbranch(cond, iftrue, iffalse)
        #
        #     self.g_llvm_builder.position_at_end(iftrue)
        #     self.visit(n.iftrue)
        #     if not iftrue.is_terminated:
        #         self.g_llvm_builder.branch(ifend)
        #
        #     self.g_llvm_builder.position_at_end(iffalse)
        #     self.visit(n.iffalse)
        #     if not iffalse.is_terminated:
        #         self.g_llvm_builder.branch(ifend)
        #
        #     self.g_llvm_builder.position_at_end(ifend)
        # else:
        #     iftrue = self.g_current_function.append_basic_block()
        #     ifend = self.g_current_function.append_basic_block()
        #
        #     self.g_llvm_builder.cbranch(cond, iftrue, ifend)
        #     self.g_llvm_builder.position_at_end(iftrue)
        #     self.visit(n.iftrue)
        #     if not iftrue.is_terminated:
        #         self.g_llvm_builder.branch(ifend)
        #
        #     self.g_llvm_builder.position_at_end(ifend)

    def visit_While(self, n, status=0):
        while_cmp = self.g_current_function.append_basic_block()
        while_entry = self.g_current_function.append_basic_block()
        while_end = self.g_current_function.append_basic_block()
        self.g_loop_block_start_stack.append(while_cmp)
        self.g_loop_block_end_stack.append(while_end)

        self.g_llvm_builder.branch(while_cmp)
        self.g_llvm_builder.position_at_end(while_cmp)
        c = self.visit(n.cond, 1)
        if type(c) is not ir.IntType(1):
            c = self.g_llvm_builder.icmp_signed('!=', c, ir.Constant(c.type, 0))
        self.g_llvm_builder.cbranch(c, while_entry, while_end)

        self.g_llvm_builder.position_at_end(while_entry)
        self.visit(n.stmt)
        self.g_llvm_builder.branch(while_cmp)

        self.g_loop_block_start_stack.pop()
        self.g_loop_block_end_stack.pop()
        self.g_llvm_builder.position_at_end(while_end)

    def visit_Continue(self, n, status=0):
        self.g_llvm_builder.branch(self.g_loop_block_start_stack[-1])

    def visit_Break(self, n, status=0):
        self.g_llvm_builder.branch(self.g_loop_block_end_stack[-1])

    def visit_Return(self, n, status=0):
        if n.expr:
            ret = self.visit(n.expr, 1)
            func_ret = self.g_current_function.return_value
            if isinstance(ret.type, ir.IntType) and isinstance(func_ret.type, ir.IntType):
                if func_ret.type.width > ret.type.width:
                    ret = self.g_llvm_builder.sext(ret, func_ret.type)
                elif func_ret.type.width < ret.type.width:
                    ret = self.g_llvm_builder.trunc(ret, func_ret.type)
            self.g_llvm_builder.ret(ret)
        else:
            self.g_llvm_builder.ret_void()

    def visit_Struct(self, n, status=0):
        context = self.g_llvm_module.context
        st = context.get_identified_type(n.name)
        return st

    def visit_StructRef(self, n, status=0):
        """
            Return Struct.
            status == 0 -> get pointer
            status ==1 -> get value
        """
        if status == 0:
            if n.type == '->':
                s = self.visit(n.name, 1)

                context = self.g_llvm_module.context
                st_name = s.type.pointee.name
                st_field = n.field.name.name
                st = context.get_identified_type(st_name)
                if st_field not in self.g_type_define[st_name]:
                    raise RuntimeError("Field not defined: " + st_field)

                zero = ir.Constant(ir.IntType(32), 0)
                index = ir.Constant(ir.IntType(32), self.g_type_define[st_name].index(st_field))
                ele = self.g_llvm_builder.gep(s, [zero, index], inbounds=True)
            return ele
        elif status == 1:
            if n.type == '->':
                s = self.visit(n.name, 1)

                context = self.g_llvm_module.context
                st_name = s.type.pointee.name
                st_field = n.field.name.name
                st = context.get_identified_type(st_name)
                if st_field not in self.g_type_define[st_name]:
                    raise RuntimeError("Field not defined: " + st_field)

                zero = ir.Constant(ir.IntType(32), 0)
                index = ir.Constant(ir.IntType(32), self.g_type_define[st_name].index(st_field))
                ele = self.g_llvm_builder.gep(s, [zero, index], inbounds=True)
                ele = self.g_llvm_builder.load(ele)
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
        self.g_global_variable[nam] = \
            ir.GlobalVariable(self.g_llvm_module, typ, name=nam)
        # allocate
        if n.init:
            self.g_global_variable[nam].initializer = self.global_visit(n.init, n.name)
        pass

    def global_visit_ArrayDecl(self, n, status=0):
        d = self.get_type(n.type)
        nam = d['dname']
        typ = d['dtype']
        self.g_global_variable[nam] = \
            ir.GlobalVariable(self.g_llvm_module, ir.ArrayType(typ, int(n.dim.value)), name=nam)
        return self.g_global_variable[nam]

    def global_visit_TypeDecl(self, n, status=0):
        if isinstance(n.type, ast.Struct):
            typ = self.global_visit(n.type)
            if n.declname:
                nam = n.declname
                self.g_global_variable[nam] = \
                    ir.GlobalVariable(self.g_llvm_module, typ, name=nam)
                return self.g_global_variable[nam]
            return None
        else:
            typ = self.visit(n.type)
            nam = n.declname
            self.g_global_variable[nam] = \
                ir.GlobalVariable(self.g_llvm_module, typ, name=nam)
            return self.g_global_variable[nam]

    def global_visit_InitList(self, n, status=0):
        # arr = ir.Constant(ir.ArrayType(typ, int(len(n.exprs)))
        return ir.Constant.literal_array([self.visit(ele) for ele in n.exprs])

    def global_visit_Constant(self, n, status=0):
        return self.visit(n)

    def global_visit_Struct(self, n, status=0):
        context = self.g_llvm_module.context
        st = context.get_identified_type(n.name)
        elements = [self.get_decl(it) for it in n.decls]
        types = [ele['dtype'] for ele in elements]
        self.g_type_define[n.name] = [ele['dname'] for ele in elements]
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
                    args.append(self.visit(arg, status=1))

            return self.g_llvm_module.declare_intrinsic(n.name.name, (), func_type), args

        if n.name.name == 'gets':
            func_type = ir.FunctionType(ir.IntType(32), [], var_arg=True)
            args = []
            for arg in n.args.exprs:
                zero = ir.Constant(ir.IntType(32), 0)
                ptr = self.g_llvm_builder.gep(self.visit(arg, status=0), [zero, zero], inbounds=True)
                args.append(ptr)

            return self.g_llvm_module.declare_intrinsic(n.name.name, (), func_type), args

        if n.name.name == 'isdigit':
            func_type = ir.FunctionType(ir.IntType(32), [ir.IntType(32)], var_arg=False)
            args = []
            for arg in n.args.exprs:
                ext = self.g_llvm_builder.sext(self.visit(arg, status=1), ir.IntType(32))
                args.append(ext)
            return self.g_llvm_module.declare_intrinsic(n.name.name, (), func_type), args

        if n.name.name == 'atoi':
            func_type = ir.FunctionType(ir.IntType(32), [], var_arg=True)
            args = []
            for arg in n.args.exprs:
                zero = ir.Constant(ir.IntType(32), 0)
                ptr = self.g_llvm_builder.gep(self.visit(arg, status=0), [zero, zero], inbounds=True)
                args.append(ptr)

            return self.g_llvm_module.declare_intrinsic(n.name.name, (), func_type), args

        if n.name.name == 'memcpy':
            args = []
            for index, arg in enumerate(n.args.exprs):
                if index == 2:
                    args.append(self.visit(arg, status=1))
                else:
                    array_addr = self.visit(arg, status=0)
                    if isinstance(array_addr.type, ir.PointerType) and \
                            isinstance(array_addr.type.pointee, ir.ArrayType):
                        zero = ir.Constant(ir.IntType(32), 0)
                        array_addr = self.g_llvm_builder.gep(array_addr, [zero, zero], inbounds=True)
                    args.append(array_addr)
            args.append(ir.Constant(ir.IntType(32), 1))
            args.append(ir.Constant(ir.IntType(1), 0))

            pint8 = ir.PointerType(ir.IntType(8))
            k = self.g_llvm_module.declare_intrinsic('llvm.memcpy', [pint8, pint8, ir.IntType(32)]), args
            return k

        if n.name.name == 'strlen':
            func_type = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=False)
            args = []
            for arg in n.args.exprs:
                zero = ir.Constant(ir.IntType(32), 0)
                ptr = self.g_llvm_builder.gep(self.visit(arg, status=0), [zero, zero], inbounds=True)
                args.append(ptr)

            return self.g_llvm_module.declare_intrinsic(n.name.name, (), func_type), args

    def get_element(self, n, arg=None):
        if arg:
            typ = type(n)
            if typ == ast.PtrDecl:
                return ir.PointerType(arg)
            elif typ == ast.ArrayDecl:
                return ir.ArrayType(arg, int(n.dim.value))
            elif typ == ast.FuncDecl:
                if n.args:
                    paramtypes = [self.generate_declaration(param, status=2) for param in n.args.params]
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
            elif n in self.g_type_define:
                context = self.g_llvm_module.context
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
            decl = motifiers.pop(0)
            name = decl.name
            for m in motifiers:
                current = self.get_element(m, current)

            if status == 0:
                self.g_named_memory[n.name] = self.g_llvm_builder.alloca(current, name=name)
            elif status == 1:
                self.g_global_variable[name] = \
                    ir.GlobalVariable(self.g_llvm_module, current, name=name)
                self.g_global_variable[name].initializer = ir.Constant(current, None)
            elif status == 2:
                if len(motifiers) > 0 and type(motifiers[0]) == ast.FuncDecl:
                    function = ir.Function(self.g_llvm_module, current, name=name)
                    if motifiers[0].args:
                        paranames = [param.name for param in motifiers[0].args.params]
                        for arg, arg_name in zip(function.args, paranames):
                            arg.name = arg_name
                            # Add arguments to variable symbol table.
                            self.g_named_argument[arg_name] = arg
                            # Set signed extension for char
                            if isinstance(arg.type, ir.IntType) and arg.type.width == 8:
                                arg.add_attribute('signext')
                    self.g_named_function[name] = function
                    return function
                else:
                    return current

        elif typ == ast.Struct:
            context = self.g_llvm_module.context
            current = context.get_identified_type(n.name)

            # define struct
            if n.name not in self.g_type_define:
                self.g_type_define[n.name] = [ele.name for ele in n.decls]
                types = [self.generate_declaration(ele, status=2) for ele in n.decls]
                current.set_body(*types)

            decl = motifiers.pop(0)
            name = decl.name
            for m in motifiers:
                current = self.get_element(m, current)

            if status == 0:
                return current
            elif status == 1:
                self.g_global_variable[name] = \
                    ir.GlobalVariable(self.g_llvm_module, current, name=name)
                self.g_global_variable[name].initializer = ir.Constant(current, None)

            elif len(motifiers) > 0 and type(motifiers[0]) == ast.FuncDecl:
                function = ir.Function(self.g_llvm_module, current, name=name)
                paranames = [param.name for param in motifiers[0].args]
                for arg, arg_name in zip(function.args, paranames):
                    arg.name = arg_name
                    # Add arguments to variable symbol table.
                    self.g_named_argument[arg_name] = arg
                self.g_named_function[name] = function
                return function
            else:
                return current

        elif typ in {ast.ArrayDecl, ast.FuncDecl, ast.PtrDecl, ast.Decl}:
            return self.generate_declaration(n.type, status, motifiers+[n])

    def remove_quotes(self, str):
        return str[1:-1]

    def char2int(self, str):
        return  ord(self.remove_quotes(str))

    # ---------- check & handle error ----------

    def declaration_verify(self, name):
        if name in self.g_named_memory.keys() \
                or name in self.g_named_argument.keys() \
                or name in self.g_global_variable.keys():
            raise RuntimeError("Duplicate variable declaration!")

    def reference_verify(self, name, type):
        pass

