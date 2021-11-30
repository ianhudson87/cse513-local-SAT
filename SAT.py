class Formula:
    def __init__(self, formula, formula_type):
        # formula looks like: [[-1, 2], [3, -2]]
        # CNF:(not x_1 OR x_2) AND (x_3 OR not x_2)
        # DNF:(not x_1 AND x_2) OR (x_3 AND not x_2)
        if formula_type not in ["CNF", "DNF"]:
            raise ValueError("not a valid type")
        
        self.formula = formula
        self.formula_type = formula_type

        self.variables = set([abs(val) for inner in formula for val in inner])
        if 0 in self.variables:
            raise ValueError("don't use 0 as a variable")
        self.num_variables = len(self.variables)

    def check_assignment(self, assignments):
        # assignment looks like: {1:True, 2:False, 3:False} -> x_1=True, x_2=False, x_3=False
        variables = assignments.keys()
        if set(variables) != self.variables:
            raise ValueError("variables don't match up with formula")

        if self.formula_type == "DNF":
            # make sure every clause has at least 1 satisfied literal
            for clause in self.formula:
                found_satisfied_literal = False # for this clause
                for literal in clause:
                    if is_literal_satisfied(literal, assignments):
                        # found satisfied literal for this clause
                        found_satisfied_literal = True
                        break

                if not found_satisfied_literal:
                    # there exists a clause with no satisfied literals
                    return False

            # went through all clauses and always found at least 1 satisfied literal
            return True

        if self.formula_type == "CNF":
            # see if some term has all of its literals satisfied
            for term in self.formula:
                all_literals_satisfied = True
                for literal in term:
                    if not is_literal_satisfied(literal, assignments):
                        # term has unsatisfied literal, try next term
                        all_literals_satisfied=False
                        break
                
                if all_literals_satisfied:
                    # this term has all of its literals satisfied
                    return True

            # no term has all of its literals satisfied
            return False

def is_literal_satisfied(literal, assignments):
    variable = abs(literal) # which variable the literal has
    variable_assignment = assignments[variable]
    if (variable_assignment is True and literal>0) or (variable_assignment is False and literal<0):
        return True
    return False

f = Formula([[-1, 2], [3, -2]], formula_type="CNF")
# print(f.num_variables)
y = f.check_assignment({2:True, 3:False, 1:False})
print(y)