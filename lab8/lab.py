"""6.009 Lab 8B: carlae Interpreter Part 2"""

# REPLACE THIS FILE WITH YOUR lab.py FROM LAB 8A, WHICH SHOULD BE THE
# STARTING POINT FOR THIS LAB.

import sys
import doctest
# NO ADDITIONAL IMPORTS!
# IN ADDITION, DO NOT USE sys OTHER THAN FOR THE THINGS DESCRIBED IN THE LAB WRITEUP

# import os
# import json

class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass


class Environment:
    def __init__(self, parent):
        """
        intialize values for environment:
            map: map variables to their values
            parent: point to the parent env
        """
        self.map = {}
        self.parent = parent

    def new_var(self, var, val):
        """
        add a new var or reset var to val in this environment
        """
        self.map[var] = val

    def init_env(self, var):
        """
        Finding the nearest enclosing environment in which var is defined 
        (starting from self and working upward until it finds a binding)
        Return None if not found
        """
        while self is not None:
            if var in self.map:
                return self
            self = self.parent
        return None


class Function:
    def __init__(self, params, function, env):
        """
        intialize values for function
            params: list of parameters        
            function: function's body
            env: the function is defined in this environment
        """
        self.params = params
        self.function = function
        self.env = env


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def copy(self):
        """
        return a copy of self
        Return:
            self_copy (Pair)
        """
        self_copy = Pair(self.car, None)
        temp = self_copy
        while self.cdr is not None:
            self = self.cdr
            temp.cdr = Pair(self.car,None)
            temp = temp.cdr
        return self_copy

    def length(self):
        """
        return the length of self
        Return:
            l (int)
        """
        l = 1
        while self.cdr is not None:
            l += 1
            self = self.cdr
        return l

    def indexing(self, k):
        """
        return the value at index k in self
        Parameter:
            k (int): index
        Return: 
            the value at the kth index
        """
        i = 0
        while i != k:
            self = self.cdr
            i += 1
        return self.car

    def concat(self, next_ll):
        """
        concatinate self with next_ll
        Parameter:
            next_ll (Pair)
        Return:
            next_self (Pair)
        """
        if next_ll is None:
            return self

        next_self = self
        temp = next_self
        while self.cdr is not None:         
            temp = temp.cdr
            self = self.cdr
        temp.cdr = next_ll
        return next_self

    def map(self, f):
        """
        apply function f to each value in the linked list self
        Parameter:
            f: a function
        Return:
            result (Pair)
        """
        result = Pair(evaluate_function(f, [self.car]), None)
        new_res = result
        while self.cdr is not None:
            self = self.cdr
            new_res.cdr = Pair(evaluate_function(f, [self.car]), None)
            new_res = new_res.cdr
        return result

    def filter(self, f):
        """
        apply filter f to the linked list self
        Parameter:
            f: a function
        Return:
            ans (Pair) or None
        """
        # first apply map to self, then takes out the elements that are mapped to True
        all_result = self.map(f)
        while all_result is not None:
            # self.car is mapped to True, then add it to new_result
            if all_result.car:
                try:
                    new_result.cdr = Pair(self.car, None)
                    new_result = new_result.cdr
                except:
                    new_result = Pair(self.car, None)
                    ans = new_result
            all_result = all_result.cdr
            self = self.cdr
        try:
            return ans
        except:
            return None

    def reduce(self, f, initval):
        """
        suppose self is [x_1, x_2,..., x_n], return f(x_n, f(x_n-1,...,f(x_1, initval)...))
        Parameters:
            f: function
            initval: a value
        Return:
            ans: value of f(x_n, f(x_n-1,...,f(x_1, initval)...))
        """
        ans = initval
        while self is not None:
            ans = evaluate_function(f, [ans, self.car])
            self = self.cdr
        return ans

#################### LEXER AND PARSER ########################################

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.top

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    >>> tokenize("(cat (dog (tomato)))")
    ['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']
    >>> tokenize("(foo (bar 3.14))")
    ['(', 'foo', '(', 'bar', '3.14', ')', ')']
    """
    tokens = []
    # if source has multiple lines
    source_list = source.splitlines()
    for line in source_list:
        unit = ''
        for char in line:
            # ignore everything after ';'
            if char == ';':
                if len(unit) > 0:
                    tokens.append(unit)
                    unit = ''
                break
            # if it's ')' or '(', add the unit before it and then this parenthesis
            if char == ')' or char == '(':
                if len(unit) > 0:
                    tokens.append(unit)
                    unit = ''
                tokens.append(char)
            elif char == ' ':
                if len(unit) > 0:
                    tokens.append(unit)
                    unit = ''
            else:
                unit += char
        # add the last unit on the current line
        if len(unit) > 0:
            tokens.append(unit)
            unit = ''
    # add the last unit in source
    if len(unit) > 0:
        tokens.append(unit)
    return tokens

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists
    Arguments:
        tokens (list): a list of strings representing tokens

    >>> s = '(define circle-area (lambda (r) (* 3.14 (* r r))))'
    >>> tokens = tokenize(s)
    >>> parse(tokens)
    ['define', 'circle-area', ['lambda', ['r'], ['*', 3.14, ['*', 'r', 'r']]]]

    >>> tokens = tokenize("(cat (dog (tomato)))")
    >>> parse(tokens)
    ['cat', ['dog', ['tomato']]]

    >>> parse(['2'])
    2

    >>> parse(['x'])
    'x'

    >>> parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')'])
    ['+', 2, ['-', 5, 3], 7, 8]
    """
    # if this doesn't contain any S-expression, then it must be a single symbol or number
    if len(tokens) == 0:
        return []   
    # check if the parentheses are proper 
    diff = 0
    for i, c in enumerate(tokens):
        if c == '(':
            diff += 1
        elif c == ')':
            diff -= 1
        if diff < 0:
            raise SyntaxError
        if diff == 0 and i != len(tokens)-1:
            raise SyntaxError
    if diff != 0:
        raise SyntaxError
    parsed = recurse_parse(tokens)
    return parsed[0]

def recurse_parse(tokens):
    """
    helper function; parse tokens recursively 
    """
    # base case
    if tokens == []:
        return tokens

    first_unit = tokens[0]

    # it's an S-expression
    if first_unit == '(':
        # start parent counter
        diff = 1
        for end_i, val in enumerate(tokens[1:]):
            if val == '(':
                diff+=1
            if val == ')':
                diff-=1
            if diff == 0:
                break
        # at the end of the loop, end_i is the index for which the parenthesis is closed
        end_i += 1 
        # recurse
        # if tokens=['(',xxxx,')',yyyy], then recurse on [xxxx] and [yyyy]
        return [recurse_parse(tokens[1:end_i])] + recurse_parse(tokens[end_i+1:])

    # if it's a symbol or number
    new_first = first_unit
    try: # check if it's an int
        new_first = int(first_unit)
    except:
        try: # check if it's a float
            new_first = float(first_unit)
        except: # otherwise it's a str
            new_first = first_unit
    return [new_first] + recurse_parse(tokens[1:])

############################### EVALUATE ########################################

def mult(args):
    """
    take arbitrarily-many arguments and should return the product of all its arguments.
    """
    if len(args) == 0:
        return 1
    prod = 1
    for arg in args:
        prod = prod * arg
    return prod

def div(args):
    """
    return the result of successively dividing the first argument by the remaining arguments.
    """
    denominator = mult(args[1:])
    return args[0]/denominator

def length(args):
    """
    (length LIST) should take a list as argument and should return 
    the length of that list. When called on any object that is not a linked list, 
    it should raise an EvaluationError
    """
    ll = args[0]
    try:
        if ll is None:
            return 0
        return ll.length()
    except:
        raise EvaluationError

def elt_at_index(args):
    """
    (elt-at-index LIST INDEX) should take a list and a nonnegative index, 
    and it should return the element at the given index in the given list. 
    As in Python, indices start from 0. If LIST is a cons cell (but not a list),
    then asking for index 0 should produce the car of that cons cell, 
    and asking for any other index should raise an EvaluationError
    """
    try:
        ll, index = args
        return ll.indexing(index)
    except:
        raise EvaluationError

def concat(args):
    """
    (concat LIST1 LIST2 LIST3 ...) should take an arbitrary number of lists as arguments 
    and should return a new list representing the concatenation of these lists. 
    If exactly one list is passed in, it should return a copy of that list. 
    If concat is called with no arguments, it should produce an empty list. 
    Calling concat on any elements that are not lists should result in an EvaluationError.
    """
    first_ll = None
    # make a copy of the first non empty linked list ll
    for i, ll in enumerate(args):
        if ll is not None:
            first_ll = ll.copy()
            break
    # if all linked lists are empty, then return None
    if first_ll is None:
        return None
    # then concatenate with each non empty linked list
    for ll in args[i+1:]:
        if ll is None:
            continue
        try:
            first_ll = first_ll.concat(ll.copy())
        except:
            raise EvaluationError
    return first_ll

def map_list(args):
    """
    (map FUNCTION LIST) takes a function and a list as arguments, and it returns a new list
    containing the results of applying the given function to each element of the given list.
    """
    try:
        f, ll = args
        if ll is None:
            return None
        return ll.map(f)
    except:
        raise EvaluationError

def filter_list(args):
    """
    (filter FUNCTION LIST) takes a function and a list as arguments, and it returns a new list 
    containing only the elements of the given list for which the given function returns true.
    """
    try:
        f, ll = args
        if ll is None:
            return None
        return ll.filter(f)
    except:
        raise EvaluationError

def reduce_list(args):
    """
    (reduce FUNCTION LIST INITVAL) takes a function, a list, and an initial value as inputs. 
    It produces its output by successively applying the given function to the elements in the list, 
    maintaining an intermediate result along the way
    """
    try:
        f, ll, initval = args
        if ll is None:
            return initval
        return ll.reduce(f, initval)
    except:
        raise EvaluationError

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': mult,
    '/': div,
    '=?': lambda args: all(args[i] == args[i+1] for i in range(len(args)-1)),
    '>': lambda args: all(args[i] > args[i+1] for i in range(len(args)-1)),
    '>=': lambda args: all(args[i] >= args[i+1] for i in range(len(args)-1)),
    '<': lambda args: all(args[i] < args[i+1] for i in range(len(args)-1)),
    '<=': lambda args: all(args[i] <= args[i+1] for i in range(len(args)-1)),
    '#t': True,
    '#f': False,
    'length': length,
    'elt-at-index': elt_at_index,
    'concat': concat,
    'map': map_list,
    'filter': filter_list,
    'reduce': reduce_list
}

def evaluate_variable(var, env):
    """
    helper to evaluate a var in the given environment
    If the name has a binding in the environment, that value is returned.
    If the name does not have a binding in the environment and the environment has a parent, we look up the name in the parent environment (following these same steps).
    If the name does not have a binding in the environment and the environment does not have a parent, an EvaluationError is raised.
    """
    env_copy = env
    # while we have not found the env where the var is last modified
    while env_copy != None:
        # if the var is last modified in this env, return it
        if var in env_copy.map:
            return env_copy.map[var]
        # move up the parent pointer
        else:
            env_copy = env_copy.parent
    raise EvaluationError

def evaluate_function(keyword, args):

    """
    helper to evaluate a function given a keyword and the params
    to evaluate
    """
    # if this is a basic keyword in builtins, evaluate builtin
    if keyword in carlae_builtins.values():
        return keyword(args)
    # if it's not a function or have different parameters, raise Error
    elif not isinstance(keyword, Function) or len(keyword.params) != len(args):
        raise EvaluationError
    # otherwise it's a user-defined function
    else:
        # create working environemnt
        curr_env = Environment(keyword.env)
        # evaluate each parameter at the given arg
        for i in range(len(args)):
            evaluate(['define', keyword.params[i], args[i]], curr_env)
        # evaluate this function in the environment with updated parameters
        return evaluate(keyword.function, curr_env)


def evaluate_define(var, args, env):
    """
    handle the case when the user defines a function or a variable
    """
    #  if the NAME in a define expression is itself an S-expression, it is implicitly translated to a function definition before binding.
    if isinstance(var, list):
        # change the representation to a lambda function
        # evaluate and get function
        val = evaluate(['lambda', var[1:], args], env)
        # add this function 
        env.new_var(var[0], val)

    # otherwise it's defined in the traditional way
    else:
        # evaluate and then add the variable
        val = evaluate(args, env)
        env.new_var(var, val)
    return val

def boolean_combinators(bool_sym, args_list, env=None):
    """
    >>> s = '(and (> 3 2) (< 7 8) #f)'
    >>> L = parse(tokenize(s))
    >>> boolean_combinators(L[0],L[1:])
    False

    >>> s = '(or (> 3 2) #t (< 4 3))'
    >>> L = parse(tokenize(s))
    >>> boolean_combinators(L[0],L[1:])
    True

    >>> s = '(not (=? 2 3))'
    >>> L = parse(tokenize(s))
    >>> boolean_combinators(L[0],L[1:])
    True

    """
    # evaluates to true if all of its arguments are true.
    if bool_sym == 'and':
        for args in args_list:
            if not evaluate(args, env):
                return False
        return True

    # evaluates to true if any of its arguments is true.
    elif bool_sym == 'or':
        for args in args_list:
            if evaluate(args,env):
                return True 
        return False

    # evaluate to false if its argument is true
    elif bool_sym == 'not':
        for args in args_list:
            if not evaluate(args, env):
                return True
        return False

def evaluate_list(args, env=None):
    """
    take zero or more arguments and should construct a linked list that contains those arguments, in order.
    """
    # base case empty []
    if len(args) == 0:
        return None
    # base case [args[0]]
    elif len(args) == 1:
        return evaluate(['cons', args[0], 'nil'], env)
    return evaluate(['cons', args[0], ['list']+args[1:]], env)

def recurse_evaluate(tree, env = None):
    """ 
    recursive helper for evaluate
    """
    # if tree is in a base case, return it
    if tree is None or isinstance(tree, int) or isinstance(tree, float) or isinstance(tree, Pair) or isinstance(tree, Function):
        return tree

    # if tree is a string, check if we can evaluate the variable in env
    elif isinstance(tree, str):
        if tree == 'nil':
            return None
        try:
            return evaluate_variable(tree, env)
        except:
            raise EvaluationError

    # if tree is a list, do things with components
    elif isinstance(tree, list):
        # if tree is empty, raise error
        if not tree:
            raise EvaluationError        
  
        keyword = tree[0] # keyword is either a special form or a function
            
        # evaluate (define name expr)
        if keyword == 'define':
            name, expr = tree[1], tree[2]
            return evaluate_define(name, expr, env)

        # evaluate (lambda (param1 param2 ...) expr)
        elif keyword == 'lambda':
            # params is the list of the function's parameters, in order.
            # expr is the function's body is the expression (+ x y).
            # the function was defined in the environment env.
            params, expr = tree[1], tree[2]
            function = Function(params, expr, env)
            return function

        # evaluate boolean combinators ex. ('and' arg1 arg2 ...)
        elif keyword in ['and', 'or', 'not']:
            return boolean_combinators(keyword,tree[1:], env)

        # evaluate conditionals (if cond trueexp falseexp)
        #  If COND evaluates to true, the result of this expression is the result of evaluating TRUEEXP; 
        # if COND instead evaluates to false, the result of this expression is the result of evaluating FALSEEXP.
        elif keyword == 'if':
            cond, trueexp, falseexp = tree[1], tree[2], tree[3]
            if evaluate(cond,env):
                return evaluate(trueexp,env)
            else:
                return evaluate(falseexp,env)

        # (cons 1 2) should result in a new Pair object whose car is 1 and whose cdr is 2
        elif keyword == 'cons':
            car = evaluate(tree[1], env)
            cdr = evaluate(tree[2], env)
            pair = Pair(car, cdr)
            return pair

        # (car X) should take a cons cell (an instance of your Pair class) as argument and 
        # should return the first element in the pair. If it is called on something that is not a cons cell, it should raise an EvaluationError.
        elif keyword == 'car':
            X = evaluate(tree[1],env)
            if isinstance(X, Pair):
                return X.car
            raise EvaluationError

        elif keyword == 'cdr':
            X = evaluate(tree[1],env)
            if isinstance(X, Pair):
                return X.cdr
            raise EvaluationError
            
        elif keyword == 'list':
            return evaluate_list(tree[1:], env)

        # begin should simply return its last argument
        elif keyword == 'begin':
            args = tree[1:][:]
            for i, arg in enumerate(args):
                if i == len(args)-1:
                    return evaluate(arg,env)
                evaluate(arg,env)

        # evaluate (let ((VAR1 VAL1) (VAR2 VAL2) (VAR3 VAL3) ...) BODY)
        # Evaluating all the given values in the current environment
        # Creating a new environment whose parent is the current environment, and binding each name to its associated value in this new environment.
        # Evaluating the BODY expression in this new environment (this value is the result of evaluating the let special form)
        elif keyword == 'let':
            new_env = Environment(env)
            expr, body = tree[1], tree[2]
            for pair in expr:
                var, val = pair                
                new_env.new_var(var, evaluate(val, env))
            return evaluate(body, new_env)

        # evaluate (set! VAR EXPR)
        # Evaluating the given expression in the current environment
        # Finding the nearest enclosing environment in which VAR is defined (starting from the current environment 
        # and working upward until it finds a binding), and updating its binding in that environment to be the result of evaluating EXPR
        elif keyword == 'set!':
            var, expr = tree[1], tree[2]
            new_val = evaluate(expr, env)
            new_env = env.init_env(var)
            new_env.new_var(var, new_val)
            return new_val

        # evaluate (f expr1 expr2 ...)
        # Otherwise, e is a compound expression representing a function call. Each of the subexpressions should be evaluated in the given environment, and:
        # If the first subexpression is a built-in function, it should be called with the remaining subexpressions as arguments (in order).
        # If the first subexpression is a user-defined function, it should be called according to the rules given above.
        else:
            try:
                # get the function of the keyword
                function = evaluate(keyword, env)
                args = []
                # for every value in the rest
                for val in tree[1:]:
                    # evaluate this val to get value
                    v = evaluate(val, env)
                    # add this to the args
                    args.append(v)
                # evaluate this function with these args
                return evaluate_function(function, args)
            except:
                raise EvaluationError

    raise EvaluationError

def initialize_env():
    """
    None -> builtins -> env 
    """
    builtins = Environment(None)
    builtins.map = carlae_builtins
    env = Environment(builtins)
    return env

def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.
    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

    # create env
    if env is None:
        env = initialize_env()
    # evaluate recursively
    return recurse_evaluate(tree, env)


def result_and_env(tree, env = None):
    """
    function to return both the result and current environment
    """
    if env is None:
        env = initialize_env()
    result = evaluate(tree, env)
    return (result, env)


def evaluate_file(fname, env = None):
    """
    take a single argument (a string containing the name of a file to be evaluated) and an optional argument 
    (the environment in which to evaluate the expression), and return the result of evaluating the expression contained in the file 
    """
    file = open(fname)
    expr = ' '.join(line.strip() for line in file)
    file.close()
    return evaluate(parse(tokenize(expr)), env)


def REPL():
    inp = input('in> ')
    

    while inp != 'QUIT':
        try:
            print('out> ', evaluate(parse(tokenize(inp)),env))
        except:
            print('ERROR!')
        inp = input('in> ')


############################## HELPER FUNCTIONS FOR DEBUGGING #################
# def load_test_values(n):
#     """
#     Helper function to load test inputs/outputs
#     """
#     with open('test_inputs/%s.json' % n) as f:
#         inputs = json.load(f)

#     return inputs

# nil_rep = None
# def list_from_ll(ll):
#     if isinstance(ll, Pair):
#         if ll.cdr == nil_rep:
#             return [list_from_ll(ll.car)]
#         return [list_from_ll(ll.car)] + list_from_ll(ll.cdr)
#     elif ll == nil_rep:
#         return []
#     elif isinstance(ll, (float, int)):
#         return ll
#     else:
#         return 'SOMETHING'

# def individual_test_case(n):
#   inp = load_test_values(n)
#   env = initialize_env()
#   for inp_list in inp:
#       try:
#           result = evaluate(inp_list, env)
#           print(list_from_ll(result))
#       except:
#           print('error', inp_list)

if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    env = initialize_env()

    for fname in sys.argv[1:]:
        print(evaluate_file(fname, env))
    REPL()
    # uncommenting the following line will run doctests from above

    # print(individual_test_case(70))
    doctest.testmod()


    pass





