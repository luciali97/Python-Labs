import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    # override the behavior of the following 8 operations
    def __add__(self, other):
        return Add(self, other)
    def __radd__(self, other):
        return Add(other, self)
    def __sub__(self, other):
        return Sub(self, other)
    def __rsub__(self, other):
        return Sub(other, self)
    def __mul__(self, other):
        return Mul(self, other)
    def __rmul__(self, other):
        return Mul(other, self)
    def __div__(self, other):
        return Div(self, other)
    def __rdiv__(self, other):
        return Div(other, self)

    def equal(self, n):
        """
        Check if self == Num(n)
        """
        if isinstance(self, Num): 
            if self.n == n:
                return True
        return False


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'

    def deriv(self, x):
        """
        d/dx x = 1 and d/dy x = 0
        """
        if x == self.name:
            return Num(1)
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        if self.name in mapping.keys():
            return mapping[self.name]
        return self


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'

    def deriv(self, x):
        """
        d/dx c = 0
        """
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return self.n

class BinOp(Symbol):
    def __init__(self, left, right):
        """
        Initializer

        left (Symbol, int, str): representing the left-hand operand
        right (Symbol, int, str): representing the right-hand operand
        """
        
        # check if the arguments passed to the constructor are str or int
        if isinstance(left, str):
            left_op = Var(left)
        elif isinstance(left, int):
            left_op = Num(left)
        else:
            left_op = left

        if isinstance(right, str):
            right_op = Var(right)
        elif isinstance(right, int):
            right_op = Num(right)
        else:
            right_op = right

        self.left = left_op
        self.right = right_op
        self.opsymb = 'op'
        self.opname = 'BinOp'

    def __str__(self):
        """
        >>> z = Add(Var('x'), Sub(Var('y'), Num(2)))
        >>> str(z)
        'x + y - 2'
        >>> str(Mul(Var('x'), Add(Var('y'), Var('z'))))
        'x * (y + z)'
        """
        left_str = str(self.left)
        right_str = str(self.right)

        # if B.left and/or B.right themselves represent expressions with lower precedence than B,
        # wrap their string representations in parentheses
        if self.opsymb == '*' or self.opsymb == '/':
            if isinstance(self.left, Add) or isinstance(self.left, Sub):
                left_str = '(' + left_str + ')'
            if isinstance(self.right, Add) or isinstance(self.right, Sub):
                right_str = '(' + right_str + ')'

        # if B represents a subtraction or a division and B.right represents an expression with 
        # the same precedence as B, wrap B.right's string representation in parentheses.
        if self.opsymb == '/' and (isinstance(self.right, Mul) or isinstance(self.right, Div)):
            right_str = '(' + right_str + ')'
        if self.opsymb == '-' and (isinstance(self.right, Add) or isinstance(self.right, Sub)):
            right_str = '(' + right_str + ')'
        return left_str + ' ' + self.opsymb + ' ' + right_str

    def __repr__(self):
        """
        >>> z = Add(Var('x'), Sub(Var('y'), Num(2)))
        >>> repr(z)
        "Add(Var('x'), Sub(Var('y'), Num(2)))"
        """
        return self.opname + '(' + repr(self.left) + ', ' + repr(self.right) + ')'

    def create_op(exp1, exp2, op):
        """
        Create an appropriate instance of a subclass of BinOp (determined by op), and return that instance

        Parameters:
            exp1 (Symbol): left-hand subexpression
            exp2 (Symbol): right-hand subexpression
            op (str): one of '+', '-', '*', '/'

        Return:
            exp1 op exp2
        """
        if op == '+':
            return Add(exp1, exp2)
        elif op == '-':
            return Sub(exp1, exp2)
        elif op == '*':
            return Mul(exp1, exp2)
        elif op == '/':
            return Div(exp1, exp2)
        else:
            return None

class Add(BinOp):
    def __init__(self, left, right):       
        BinOp.__init__(self, left, right)
        self.opsymb = '+'
        self.opname = 'Add'

    def deriv(self, x):
        """
        >>> x = Var('x')
        >>> y = Var('y')
        >>> z = 2*x - x*y + 3*y
        >>> print(z.deriv('x'))
        2 * 1 + x * 0 - (x * 0 + y * 1) + 3 * 0 + y * 0
        >>> print(z.deriv('y'))
        2 * 0 + x * 0 - (x * 1 + y * 0) + 3 * 1 + y * 0
        >>> print(z.deriv('x').simplify())
        2 - y
        >>> print(z.deriv('y').simplify())
        0 - x + 3
        >>> Add(Add(Num(2), Num(-2)), Add(Var('x'), Num(0))).simplify()
        Var('x')
        """
        var = Var(x)
        return self.left.deriv(x) + self.right.deriv(x)

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        """
        Adding 0 to any expression E should simplify to E
        """
        if self.left.equal(0):
            return self.right
        if self.right.equal(0):
            return self.left
        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n + self.right.n)
        return self.left + self.right

    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)

class Sub(BinOp):
    def __init__(self, left, right):       
        BinOp.__init__(self, left, right)
        self.opsymb = '-'
        self.opname = 'Sub'

    def deriv(self, x):
        """
        d/dx (u - v) = d/dx u - d/dx v
        """
        var = Var(x)
        return self.left.deriv(x) - self.right.deriv(x)

    def simplify(self):
        """
        Subtracting 0 from any expression E should simplify to E
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if self.right.equal(0):
            return self.left
        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n - self.right.n)
        return self.left - self.right

    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)

class Mul(BinOp):
    def __init__(self, left, right):       
        BinOp.__init__(self, left, right)
        self.opsymb = '*'
        self.opname = 'Mul'

    def deriv(self, x):
        """
        d/dx (u * v) = u * d/dx v + v * d/dx u 
        """
        var = Var(x)
        return self.left * self.right.deriv(x) + self.right * self.left.deriv(x)

    def simplify(self):
        """
        Multiplying any expression E by 1 should simplify to E.
        Multiplying any expression E by 0 should simplify to 0.
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if self.left.equal(0) or self.right.equal(0):
            return Num(0)
        if self.left.equal(1):
            return self.right
        if self.right.equal(1):
            return self.left
        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n * self.right.n)
        return self.left * self.right

    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)

class Div(BinOp):
    def __init__(self, left, right):       
        BinOp.__init__(self, left, right)
        self.opsymb = '/'
        self.opname = 'Div'

    def deriv(self, x):
        """
        d/dx (u/v) = (v * d/dx u - u * d/dx v) / (v * v)
        """
        var = Var(x)
        u = self.left
        v = self.right
        return (v * u.deriv(x) - u * v.deriv(x)) / (v * v)

    def simplify(self):
        """
        Dividing any expression E by 1 should simplify to E.
        Dividing 0 by any expression E should simplify to 0.
        """
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if self.left.equal(0):
            return Num(0)
        if self.right.equal(1):
            return self.left
        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n / self.right.n)
        return Div(self.left, self.right)

    def eval(self, mapping):
        return self.left.eval(mapping)/ self.right.eval(mapping)

def tokenize(s):
    """
    Take a string as described above as input and should output a list of 
    meaningful tokens (parentheses, variable names, numbers, or operands).
    
    Parameter:
        s (str): input string
    Return:
        L (list): list of tokens

    >>> tokenize('(x * (-2 + 3))')
    ['(', 'x', '*', '(', '-2', '+', '3', ')', ')']
    """
    L = []
    w = ''
    for i, char in enumerate(s):
        if char == '-' and s[i+1] != ' ':
            w += char
        elif char == '(' or char == ')' or char == '+' or char == '-' or char =='*' or char == '/':
            if len(w) > 0:
                L.append(w)
                w = ''
            L.append(char)
        elif char != ' ':
            w += char
    if len(w) > 0:
        L.append(w)
    return L

def sym(s):
    """
    >>> sym('(x * (2 + 3))')
    Mul(Var('x'), Add(Num(2), Num(3)))
    """
    tokens = tokenize(s)
    return parse(tokens)

def parse(tokens):
    """
    Take the output of tokenize and convert it into an appropriate instance 
    of Symbol (or some subclass thereof)

    Parameter:
        tokens (list)
    Return:
        parsed_expression (Symbol)
    """
    def parse_expression(index):
        """
        recursive function that takes as argument an integer into the tokens list and returns a pair of values

        Parameter:
            index (int): the start of an expression

        Returns:
            parsed_expression (Symbol): the expression found starting at the location given by index 
            next_index (int): the index beyond where this expression ends
        """
        token = tokens[index]
        try:    # check if we can turn token into Num
            n = int(token)
            parsed_expression = Num(n)
            next_index = index + 1

        except:
            if token == '(':    # (E1 op E2)
                E1 = []
                E2 = [] 
                op = ''
                count = 0
                for i, char in enumerate(tokens):
                    if char == '(':
                        count += 1
                    elif char == ')':
                        count -= 1
                    if count  >= 1:
                        if i > 0:
                            if len(op) == 0:    # if we have not determined op yet
                                if len(E1) >= 1 and count == 1 and char != ')':
                                    op = char
                                else:
                                    E1.append(char)                   
                            else:
                                E2.append(char)
                    else:   # when count = 0, #( = #), so we have found everything
                        next_index = i + index + 1
                        break
                parsed_expression = BinOp.create_op(parse(E1), parse(E2), op)

            else:   # check if token can be turned into Var
                parsed_expression = Var(token)
                next_index = index + 1
        return parsed_expression, next_index
        
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

if __name__ == '__main__':
    doctest.testmod()
