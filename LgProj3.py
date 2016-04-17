import sys

#######################################################################
# Scanner generation
tokens = ('STR', 'CLASSNAME', 'MAKECLASS', 'SUBCLASS', 'CONCAT', 'COMP', 'VARNAME')
literals = ['.','=',]

def t_STR(t): r''' "([^"\n]|(\\"))*"|'([^'\n]|(\\'))*' '''; return t
def t_CLASSNAME(t): r''' [A-Z]+ '''; return t
def t_MAKECLASS(t): r'''makeclass '''; return t
def t_SUBCLASS(t): r'''subclass '''; return t
def t_CONCAT(t): r'''concat '''; return t
def t_COMP(t): r'''comp '''; return t
def t_VARNAME(t): r''' _[a-z]+ '''; return t

t_ignore = ' \t\r'
def t_newline(t): r'\n+'; t.lexer.lineno += t.value.count("\n")

def t_error(t):
    ''' Prints error messages when scan fails '''
    print "Illegal character at line {} '{}'".format(t.lexer.lineno, \
        t.value[0])
    t.lexer.skip(1)
    
import ply.lex as lex
lex.lex(debug=0)        # Build the lexer


######################################################################
# Parse Tree

class Node:
    """ This will store nodes in a parse tree"""
    allClassesDict = {}
    allVars = {}
    
    '''
    def __init__(self):
        self.children = []
    '''
    def doit(self):
        return "Error"
    
class MakeclassNode(Node):
    """ """
    def __init__(self, name, bodyStatements):
        self.name = name
        self.bodyStatements = bodyStatements

    def doit(self):
        Node.allClassesDict[self.name] = self

class SubclassNode(Node):
    """ """
    def __init__(self, supername, name, bodyStatements):
        self.name = name
        self.supername = supername
        self.bodyStatements = bodyStatements
        
    def doit(self):
        Node.allClassesDict[self.name] = self

class CallNode(Node):
    """ """
    def __init__(self, name):
        self.name = name

    def doit(self):
        node = Node.allClassesDict[self.name]
        result = ""
        for statement in node.bodyStatements:
            result = statement.doit()
        return node.doit()

class StringNode(Node):
    """" """
    def __init__(self, theString):
        self.value = theString[1:-1]

    def doit(self):
        print self.value
        return self.value

class ConcatNode(Node):
    """ """
    def __init__(self, leftNode, rightNode):
        self.leftNode = leftNode
        self.rightNode = rightNode

    def doit(self):
        result = self.leftNode.doit() + self.rightNode.doit()
        print result
        return result

class CompareNode(Node):
    """ """
    def __init__(self, leftNode, rightNode):
        self.leftNode = leftNode
        self.rightNode = rightNode

    def doit(self):
        result = "False"
        if self.leftNode.doit() == self.rightNode.doit():
            result = "True"
        print result
        return result

class AssignmentNode(Node):
    """" """
    def __init__(self, variablename, node):
        self.variablename = variablename
        self.node = node

    def doit(self):
        #print self.value
        Node.allVars[self.variablename] = self.node
        return Node.allVars[self.variablename]

class GetVarValueNode(Node):
    """ """
    def __init__(self, variablename):
        self.variablename = variablename

    def doit(self):
        #print self.value
        return Node.allVars[self.variablename].doit()
    
######################################################################
# Parser generation and parse tree creator

def p_statement_list_multi(p):
    " statement_list : statement_list statement "
    p[0] = p[1].append(p[2]) # returns a list

def p_statement_list_single(p):
    " statement_list : statement "
    p[0] = [p[1]] # returns a list

def p_statement_makeclass(p):
    " statement : MAKECLASS CLASSNAME statement_list '.' "
    p[0] = MakeclassNode(p[2], p[3])

def p_statement_subclass(p):
    " statement : SUBCLASS CLASSNAME CLASSNAME statement_list '.' "
    p[0] = SubclassNode(p[2], p[3], p[4])

def p_statement_expr(p):
    " statement : expr '.' "
    p[0] = p[1]

def p_statement_assign(p):
    " statement : VARNAME '=' expr '.' "
    p[0] = AssignmentNode(p[1], p[3])

def p_expr_call(p):
    " expr : CLASSNAME "
    p[0] = CallNode(p[1])

def p_expr_concat(p):
    " expr : expr CONCAT expr "
    p[0] = ConcatNode(p[1], p[3])

def p_expr_compare(p):
    " expr : expr COMP expr "
    p[0] = CompareNode(p[1], p[3])
                      
def p_expr_str(p):
    " expr : STR "
    p[0] = StringNode(p[1])

def p_expr_getvalue(p):
    " expr : VARNAME "
    p[0] = GetVarValueNode(p[1])
    
######################################################################
# Error reporting
def p_error(p):
    ''' Prints error messages when parse fails '''
    if p:
        print "Syntax error at line {} '{}'".format(p.lineno, p.value)
    else:
        print "Syntax error at EOF"

    sys.exit(-1)

import ply.yacc as yacc
yacc.yacc()              # Build parser

######################################################################
# Test driver
while 1:
    try:
        s = raw_input('calc > ')
    except EOFError:
        break
    if not s: continue
    resultList = yacc.parse(s+'\n') # parse returns None upon error
    if None != resultList:
        for x in resultList:
            print x.doit()

