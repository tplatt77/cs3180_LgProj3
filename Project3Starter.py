######################################################################
# Scanner generation
tokens = ('STR', 'CLASSNAME', 'MAKECLASS', 'VARNAME',)

literals = ['.', '=',]
def t_STR(t): r''' "([^"\n]|(\\"))*"|'([^'\n]|(\\'))*' '''; return t
def t_CLASSNAME(t): r''' [A-Z]+ '''; return t
def t_VARNAME(t): r'''_[a-z]+ '''; return t
def t_MAKECLASS(t): r'''makeclass'''; return t
t_ignore = ' \t\r'
def t_newline(t): r'\n+'; t.lexer.lineno += t.value.count("\n")

def t_error(t):
    ''' Prints error messages when scan fails '''
    print "Illegal character at line {} '{}'".format(t.lexer.lineno, \
        t.value[0])
    t.lexer.skip(1)

import ply.lex as lex
lex.lex(debug=0)       # Build the lexer

######################################################################
# Parser Tree
class Node:
    """ This will store nodes in a parse tree """

    allClassesDict = {}  # Global class string name to Node map
    allVarsDict = {}         # Global variable string name to Node map
    
    def doit(self):
        return "Error"

class MakeclassNode(Node):
    """  """
    def __init__(self, stringName, bodyStatements):
        self.name = stringName
        self.bodyStatements = bodyStatements
    
    def doit(self):
        Node.allClassesDict[self.name] = self
        return self.name

class CallClassNode(Node):
    """  """
    def __init__(self, stringName):
        self.name = stringName
    
    def doit(self):
        #print "Call : ", self.name
        node = Node.allClassesDict[self.name]
        result = ""
        for statement in node.bodyStatements:
           result = statement.doit()
        return result

class StringNode(Node):
    """  """
    def __init__(self, string_value):
        self.string_value = string_value[1:-1]  # trim quote caharcters
    
    def doit(self):
        return self.string_value

class AssignVarNode(Node):
    def __init__(self, variable_name, node):
        self.variable_name = variable_name
        self.node_value = node
    
    def doit(self):
        #print self.value
        Node.allVarsDict[self.variable_name] = self.node_value
        return self.node_value

class GetVarValueNode(Node):
    def __init__(self, variable_name):
        self.variable_name = variable_name
    
    def doit(self):
        result = Node.allVarsDict[self.variable_name].doit()
        print result
        return result

######################################################################
# Parser generation and parse tree creator
def p_statement_list_single(p):
    " statement_list : statement "
    p[0] = [p[1]] # returns a list

def p_statement_list_multi(p):
    " statement_list : statement_list statement "
    p[0] = p[1].append(p[2]) # returns a list

def p_statement_makeclass(p):
    " statement : MAKECLASS CLASSNAME statement_list '.' "
    p[0] = MakeclassNode(p[2], p[3])

def p_statement_assignvar(p):
    " statement : VARNAME '=' expr '.' "
    p[0] = AssignVarNode(p[1], p[3])

def p_statement_expr(p):
    " statement : expr '.' "
    p[0] = p[1]

def p_expr_callclass(p):
    " expr : CLASSNAME "
    p[0] = CallClassNode(p[1])

def p_expr_string(p):
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
######################################################################
# Test driver
def interpret_result_list(a_result_list):
    #print resultList
    if None != a_result_list:
       [node.doit() for node in a_result_list]

import sys

if 1 < len(sys.argv):
   with open(sys.argv[1], 'r') as myfile:data=myfile.read()
   #print data
   interpret_result_list(yacc.parse(data+'\n')) # parse returns None upon error

else:
   while 1:
       try:
           s = raw_input('calc > ')
       except EOFError:
           break
       if not s: continue
      
       interpret_result_list(yacc.parse(s+'\n')) # parse returns None upon error
