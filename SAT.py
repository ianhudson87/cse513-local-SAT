import random
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
        # assignment looks like: {1:1, 2:-1, 3:1} -> x_1=True, x_2=False, x_3=False
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
    return literal * assignments[abs(literal)] > 0


class Search:
    def __init__(self, formula, hill_climb, pick, name):
        self.formula = formula # cnf formula
        self.hill_climb = hill_climb
        self.pick = pick
        self.name = name

    def general_stochastic_local_search_CNF(self, max_tries, max_flips):
        num_tries = 0
        num_final_flips = 0
        total_flips = 0
        for i in range(max_tries):
            num_tries += 1
            num_final_flips = 0
            s = {} # assignment
            for v in self.formula.variables:
                s[v] = random.choice([-1, 1])
            for j in range(1, max_flips):
                total_flips += 1
                num_final_flips += 1
                if self.formula.check_assignment(s):
                    return {"tries": num_tries, "final_flips": num_final_flips, "total_flips": total_flips}
                else:
                    possible_vars = self.hill_climb(self.formula,s)
                    x = self.pick(possible_vars)
                    s[x] = s[x] * -1
        return None
    

def Test3CNF(search, num_variables, num_clauses, num_tests):
    # generate 3CNF formula with num_variables and num_clauses
    # test to see if it is satisfiable
    # try it with the search algorithm
    test_results = {
        "tries": [],
        "final_flips": [],
        "total_flips": []
    }

    for _ in range(num_tests):
        # cnf_formula = 

        results = search.general_stochastic_local_search_CNF(9e9, 5*num_variables)
        if results is None:
            raise RuntimeError("reached max iterations")

        test_results["tries"].append(results["tries"])
        test_results["final_flips"].append(results["final_flips"])
        test_results["total_flips"].append(results["total_flips"])

    return {
        "average_tries": sum(test_results["tries"]) / num_tests,
        "average_final_flips": sum(test_results["final_flips"]) / num_tests,
        "average_total_flips": sum(test_results["total_flips"]) / num_tests
    }


f = Formula([[-1, 2], [3, -2]], formula_type="CNF")
# print(f.num_variables)
y = f.check_assignment({2:1, 3:-1, 1:-1})
print(y)