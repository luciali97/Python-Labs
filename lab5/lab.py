"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if formula is None:
        return None
    if len(formula) == 0:
        return {}

    var = formula[0][0][0]
    for sign in [True, False]:
        assign = {var: sign}

        new_formula = check_unit_clause(formula, assign)
        # if there is a contradiction, then change the assignment to var
        if new_formula is None: 
            continue 

        # recursively check if this assignment works
        new_assign = satisfying_assignment(new_formula)
        # if there is no contradiction
        if new_assign is not None:
            assign.update(new_assign)
            return assign

    return None

   
def check_unit_clause(formula, assign):
    """
    Check if the formula contains any length-one clauses ("unit" clauses)

    Parameters:
        formula (list): a cnf formula
        assign (dict): a dictionary keyed by variables and the value for each var is either True or False

    Return:
        formula (list): an updated cnf formula

    >>> check_unit_clause([[('a', True),('c', True)], [('b', True), ('a', False)]], {'b': True})
    [[('a', True), ('c', True)]]
    """

    formula = assign_literal(formula, assign)
    # if there is a contradiction
    if formula is None:
        return None

    def recurse_simplify(formula, assign,):
        if formula is None:
            return None
     
        if len(formula) == 0:
            return formula

        # check unit clause
        for clause in formula:
            if len(clause) == 1:
                var, sign = clause[0]
                assign[var] = sign

                formula = assign_literal(formula, assign)
                # if contradition
                if formula is None:
                    del assign[var]
                    return None
                return recurse_simplify(formula, assign)
        return formula

    return recurse_simplify(formula, assign)

def assign_literal(formula, assign):
    """
    Update the formula with a given assignment.

    Parameters:
        formula (list): a cnf formula
        assign (dict): a dictionary keyed by variables and the value for each var is either True or False

    Return:
        new_formula (list): an updated cnf formula

    >>> assign_literal([[('a', True),('c', True)], [('b', True), ('a', False)]], {'b': True})
    [[('a', True), ('c', True)]]
    """
    new_formula = []
    for clause in formula:
        new_clause = []
        for var, sign in clause:
            # if we need to remove the clause
            if var in assign:
                # a clause is satisfied
                if sign == assign[var]:  
                    new_clause = []
                    break
                # the only literal left in the clause cannot be satisfied
                elif len(clause) == 1: 
                    return None
            # if we don't need to remove the clause
            else:
                new_clause.append((var, sign))

        if len(new_clause) > 0:
            new_formula.append(new_clause)
    return new_formula

###################### SCHEDULING PROBLEM ##################################

def only_in_desired_rooms(student_preferences):
    """
    For each student, we guarantee that they are given a room that they selected as one of their preferences.

    Parameter:
        student_preferences (dict): dictionary mapping a student name (string) to a set of session names (strings) when that student is available

    Return: 
        cnf (list): a cnf formula expressing this constraint (students are only assigned to rooms in their preferences)
    """

    cnf = []
    if student_preferences is None:
        return []
    for student in student_preferences:
        clause = []
        for session in student_preferences[student]:
            lit = (student+'_'+session, True)
            clause.append(lit)
        cnf.append(clause)
    return cnf

def all_k_item_subset(L, k):
    """
    Get all k-item subsets of a list L

    Parameter:
        L (list): we want to find subsets of L
        k (int): the size of each subset

    Return:
        subsets (list): list of lists, where each list is a k-item subset of S
    """

    if len(L) < k:
        return []
    if len(L) == k:
        return [L]
    subsets = []
    n = len(L)

    pw = 2**n
    # return all binary numbers <= pw with k one-bits
    iteration = []
    for i in range(pw):
        binary_i = bin(i)[2:]
        num_one = 0
        for bit in binary_i:
            if bit == '1':
                num_one += 1
            if num_one > k:
                break
        if num_one == k:
            iteration.append(binary_i)

    for bin_str in iteration:
        # subset is the set corresponds to bin_str
        subset = []
        for i in range(-1, -len(bin_str)-1, -1):
            if bin_str[i] == '1':
                subset.append(L[i])
        subsets.append(subset)

    return subsets

def exactly_one_session(student_preferences, session_capacities):
    """
    Make sure that each student is assigned to at most one session.

    Parameter:
        student_preferences (dict): dictionary mapping a student name (string) to a set of session names (strings) when that student is available
        session_capacities (dict): dictionary mapping each session name to a positive integer for how many students can fit in that session.
    
    Return: 
        cnf (list): a cnf formula expressing this constraint
    """

    cnf = []
    for student in student_preferences:
        L = []
        for session in session_capacities:
            L.append((student+'_'+session, False))
        cnf_student = all_k_item_subset(L, 2)
        cnf += cnf_student
    return cnf

def no_oversubscribed_sections(student_preferences, session_capacities):
    """
    Make sure that there is no oversubscribed section.

    Parameter:
        student_preferences (dict): dictionary mapping a student name (string) to a set of session names (strings) when that student is available
        session_capacities (dict): dictionary mapping each session name to a positive integer for how many students can fit in that session.
    
    Return: 
        cnf (list): a cnf formula expressing this constraint
    """

    cnf = []
    for session in session_capacities:
        L = []
        k = session_capacities[session] + 1
        for student in student_preferences:
            L.append((student+'_'+session, False))
        cnf_session = all_k_item_subset(L, k)
        cnf += cnf_session
    return cnf

def boolify_scheduling_problem(student_preferences, session_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """

    return only_in_desired_rooms(student_preferences) + exactly_one_session(student_preferences, session_capacities) + no_oversubscribed_sections(student_preferences, session_capacities)

if __name__ == '__main__':
    print(check_unit_clause([[('a', False)], [('a', True),('c', True)], [('b', True), ('a', False)]], {'b': True, 'a': False}))
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

