import sys
class Node(object):
    """ Abstract base class for AST nodes.
    """

    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
        """ Pretty print the Node and all its attributes and
            children (recursively) to a buffer.

            buf:
                Open IO buffer into which the Node is printed.

            offset:
                Initial offset (amount of leading spaces)

            attrnames:
                True if you want to see the attribute names in
                name=value pairs. False to only see the values.

            nodenames:
                True if you want to see the actual node names
                within their parents.

            showcoord:
                Do you want the coordinates of each Node to be
                displayed.
        """
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__+ ' <' + _my_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__+ ': ')

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self,n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(' (at %s)' % self.coord)
        buf.write('\n')

        for (child_name, child) in self.children():
            child.show(
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name)


class FileAST(Node):
    def __init__(self, ext):
        self.ext = ext

    def children(self):
        nodelist = []
        for i, child in enumerate(self.ext or []):
            nodelist.append(("ext[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class Decl(Node):
    def __init__(self, name, quals, storage, spec, type, init):
        self.name = name
        self.quals = quals
        self.storage = storage
        self.spec = spec
        self.type = type
        self.init = init

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        if self.init is not None: nodelist.append(("init", self.init))
        return tuple(nodelist)

    attr_names = ('name', 'quals', 'storage', 'spec',)


class ArrayDecl(Node):
    def __init__(self, type, dim):
        self.type = type
        self.dim = dim

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        if self.dim is not None: nodelist.append(("dim", self.dim))
        return tuple(nodelist)

    attr_names = ()


class Constant(Node):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('type', 'value',)


class IdentifierType(Node):
    def __init__(self, name):
        self.name = name

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)


class InitList(Node):
    def __init__(self, exprs):
        self.exprs = exprs

    def children(self):
        nodelist = []
        for i, child in enumerate(self.exprs or []):
            nodelist.append(("exprs[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class Struct(Node):
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ('name',)


class ParamList(Node):
    def __init__(self, params):
        self.params = params

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class PtrDecl(Node):
    def __init__(self, quals, type):
        self.quals = quals
        self.type = type

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ('quals',)


class Compound(Node):
    def __init__(self, block_items):
        self.block_items = block_items

    def children(self):
        nodelist = []
        for i, child in enumerate(self.block_items or []):
            nodelist.append(("block_items[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class Assignment(Node):
    def __init__(self, op, lvalue, rvalue):
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue

    def children(self):
        nodelist = []
        if self.lvalue is not None: nodelist.append(("lvalue", self.lvalue))
        if self.rvalue is not None: nodelist.append(("rvalue", self.rvalue))
        return tuple(nodelist)

    attr_names = ('op',)


class StructRef(Node):
    def __init__(self, name, type, field):
        self.name = name
        self.type = type
        self.field = field

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.field is not None: nodelist.append(("field", self.field))
        return tuple(nodelist)

    attr_names = ('type',)


class ID(Node):
    def __init__(self, name):
        self.name = name

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)


class FuncDef(Node):
    def __init__(self, decl, param_decls, body):
        self.decl = decl
        self.param_decls = param_decls
        self.body = body

    def children(self):
        nodelist = []
        if self.decl is not None: nodelist.append(("decl", self.decl))
        if self.body is not None: nodelist.append(("body", self.body))
        for i, child in enumerate(self.param_decls or []):
            nodelist.append(("param_decls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class If(Node):
    def __init__(self, cond, iftrue, iffalse):
        self.cond = cond
        self.iftrue = iftrue
        self.iffalse = iffalse

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.iftrue is not None: nodelist.append(("iftrue", self.iftrue))
        if self.iffalse is not None: nodelist.append(("iffalse", self.iffalse))
        return tuple(nodelist)

    attr_names = ()


class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def children(self):
        nodelist = []
        if self.left is not None: nodelist.append(("left", self.left))
        if self.right is not None: nodelist.append(("right", self.right))
        return tuple(nodelist)

    attr_names = ('op',)


class Return(Node):
    def __init__(self, expr):
        self.expr = expr

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()


class ExprList(Node):
    def __init__(self, exprs):
        self.exprs = exprs

    def children(self):
        nodelist = []
        for i, child in enumerate(self.exprs or []):
            nodelist.append(("exprs[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class UnaryOp(Node):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ('op',)


class Switch(Node):
    def __init__(self, cond, stmt):
        self.cond = cond
        self.stmt = stmt

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ()


class Case(Node):
    def __init__(self, expr, stmts):
        self.expr = expr
        self.stmts = stmts

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        for i, child in enumerate(self.stmts or []):
            nodelist.append(("stmts[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()


class FuncCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.args is not None: nodelist.append(("args", self.args))
        return tuple(nodelist)

    attr_names = ()


class Break(Node):
    def __init__(self):
        pass

    def children(self):
        return ()

    attr_names = ()


class While(Node):
    def __init__(self, cond, stmt):
        self.cond = cond
        self.stmt = stmt

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ()


class ArrayRef(Node):
    def __init__(self, name, subscript):
        self.name = name
        self.subscript = subscript

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.subscript is not None: nodelist.append(("subscript", self.subscript))
        return tuple(nodelist)

    attr_names = ()


class For(Node):
    def __init__(self, init, cond, next, stmt):
        self.init = init
        self.cond = cond
        self.next = next
        self.stmt = stmt

    def children(self):
        nodelist = []
        if self.init is not None: nodelist.append(("init", self.init))
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.next is not None: nodelist.append(("next", self.next))
        if self.stmt is not None: nodelist.append(("stmt", self.stmt))
        return tuple(nodelist)

    attr_names = ()


class EmptyStatement(Node):
    def __init__(self):
        pass

    def children(self):
        return ()

    attr_names = ()


class Continue(Node):
    def __init__(self):
        pass

    def children(self):
        return ()

    attr_names = ()


class Cast(Node):
    def __init__(self, to_type, expr):
        self.to_type = to_type
        self.expr = expr

    def children(self):
        nodelist = []
        if self.to_type is not None: nodelist.append(("to_type", self.to_type))
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()


class Typename(Node):
    def __init__(self, name, quals, type):
        self.name = name
        self.quals = quals
        self.type = type

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ('name', 'quals',)


class FuncDecl(Node):
    def __init__(self, args, type):
        self.args = args
        self.type = type

    def children(self):
        nodelist = []
        if self.args is not None: nodelist.append(("args", self.args))
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ()

class PtrDecl(Node):
    def __init__(self, quals, type):
        self.quals = quals
        self.type = type

    def children(self):
        nodelist = []
        if self.type is not None: nodelist.append(("type", self.type))
        return tuple(nodelist)

    attr_names = ('quals',)

class Default(Node):
    def __init__(self, stmts):
        self.stmts = stmts

    def children(self):
        nodelist = []
        for i, child in enumerate(self.stmts or []):
            nodelist.append(("stmts[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()




