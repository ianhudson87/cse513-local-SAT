import random
from pysat.solvers import Glucose3

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
        if  0 in self.variables:
            raise ValueError("don't use 0 as a variable")
        self.num_variables = len(self.variables)
    
    # def get_scores(self, assignments):
    #     variables = assignments.keys()
    #     if set(variables) != self.variables:
    #         raise ValueError("variables don't match up with formula")

    #     if self.formula_type == "CNF":
    #         counts = {}
    #         for clause in self.formula:
    #             truth_values = [assignments[clause] for ]
    #             for literal in clause:

    def get_num_satisfied_clauses(self, assignments):
        variables = assignments.keys()
        if set(variables) != self.variables:
            raise ValueError("variables don't match up with formula")

        if self.formula_type == "CNF":
            num_satisfied_clauses = 0
            # see if clause has at least 1 satisfied literal
            for clause in self.formula:
                found_satisfied_literal = False # for this clause
                for literal in clause:
                    if is_literal_satisfied(literal, assignments):
                        # found satisfied literal for this clause
                        num_satisfied_clauses += 1
                        break

            # went through all clauses and always found at least 1 satisfied literal
            return num_satisfied_clauses

        if self.formula_type == "DNF":
            raise NotImplementedError("bad")

    def check_assignment(self, assignments):
        # assignment looks like: {1:1, 2:-1, 3:1} -> x_1=True, x_2=False, x_3=False
        variables = assignments.keys()
        if set(variables) != self.variables:
            raise ValueError("variables don't match up with formula")

        if self.formula_type == "CNF":
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

        if self.formula_type == "DNF":
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
    def __init__(self, name="name"):
        self.name = name

    def hill_climb(self, formula, assignments):
        raise NotImplementedError("implement hill climb")

    def pick(self, possible_vars):
        raise NotImplementedError("implement pick")

    def general_stochastic_local_search_CNF(self, formula, max_tries, max_flips):
        num_tries = 0
        num_final_flips = 0
        total_flips = 0
        for i in range(max_tries):
            num_tries += 1
            num_final_flips = 0
            s = {} # assignment
            for v in formula.variables:
                s[v] = random.choice([-1, 1])
            for j in range(1, max_flips):
                total_flips += 1
                num_final_flips += 1
                if formula.check_assignment(s):
                    return {"tries": num_tries, "final_flips": num_final_flips, "total_flips": total_flips}
                else:
                    possible_vars = self.hill_climb(formula,s)
                    x = self.pick(possible_vars)
                    s[x] *= -1
        return None

class GSat(Search):
    def hill_climb(self, formula, assignments):
        max_score = int(-9e5)
        items_with_max_score = []
        for variable in formula.variables:
            score_before = formula.get_num_satisfied_clauses(assignments)
            assignments[variable] *= -1
            score_after = formula.get_num_satisfied_clauses(assignments)
            assignments[variable] *= -1
            score = score_after - score_before
            if score == max_score:
                items_with_max_score.append(variable)
            elif score > max_score:
                items_with_max_score = [variable]
                max_score = score
            
        # print(items_with_max_score)
        return items_with_max_score


    def pick(self, possible_vars):
        return random.choice(possible_vars)
    

def Test3CNF(search, num_variables, num_clauses, num_tests):
    # generate 3CNF formula with num_variables and num_clauses
    # test to see if it is satisfiable
    # try it with the search algorithm
    test_results = {
        "tries": [],
        "final_flips": [],
        "total_flips": []
    }

    for i in range(num_tests):
        print(i)
        found_good_formula = False
        while not found_good_formula:
            cnf_formula = gen_formula(num_variables, num_clauses)
            g = Glucose3()
            for clause in cnf_formula:
                g.add_clause(clause)
            if g.solve():
                found_good_formula = True
        print("found_good_formula")

        formula_obj = Formula(cnf_formula, "CNF")

        results = search.general_stochastic_local_search_CNF(formula_obj, int(9e5), 5*num_variables)
        if results is None:
            raise RuntimeError("reached max iterations")
        print()

        test_results["tries"].append(results["tries"])
        test_results["final_flips"].append(results["final_flips"])
        test_results["total_flips"].append(results["total_flips"])

    return {
        "name": search.name,
        "average_tries": sum(test_results["tries"]) / num_tests,
        "average_final_flips": sum(test_results["final_flips"]) / num_tests,
        "average_total_flips": sum(test_results["total_flips"]) / num_tests
    }


def gen_formula(num_var, num_clauses):
    vars = list(range(1,num_var+1))
    formula = []
    for x in range(num_clauses):
        clause_p = random.sample(vars,3)
        formula.append([i if random.random()<=.5 else -1*i for i in clause_p])
    return formula



f = Formula([[-1, 2], [3, -2]], formula_type="CNF")
# print(f.num_variables)
y = f.check_assignment({2:1, 3:-1, 1:-1})
print("here", y)

num_vars = 10
print(len(gen_formula(num_vars, int(num_vars * 4.3))))

#3CNF, num var, num clauses

gsat_search = GSat("gsat")
num_vars = 50
print(Test3CNF(gsat_search, num_vars, int(num_vars * 4.3), 10))