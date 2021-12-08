import random
from pysat.solvers import Glucose3
import statistics
import json

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
    
    def get_scores(self, assignments):
        scores = {}
        for variable in self.variables:
          scores[variable] = 0
        for clause in self.formula:
          num_true = 0
          for literal in clause:
            if is_literal_satisfied(literal, assignments):
              num_true += 1
          if num_true <= 1:
            for literal in clause:
              if num_true == 0:
                scores[abs(literal)] += 1
              elif num_true == 1 and is_literal_satisfied(literal, assignments):
                  scores[abs(literal)] -= 1
        return scores

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
        scores = formula.get_scores(assignments)
        for variable, score in scores.items():
            if score == max_score:
                items_with_max_score.append(variable)
            elif score > max_score:
                items_with_max_score = [variable]
                max_score = score
            
        # print(items_with_max_score)
        return items_with_max_score

    def pick(self, possible_vars):
        return random.choice(possible_vars)

class TSat(Search):
    def hill_climb(self, formula, assignments):
        scores = formula.get_scores(assignments)
        vars_positive_scores = [var for var, score in scores.items() if score>0]
        if len(vars_positive_scores)>0:
            return vars_positive_scores
        
        vars_zero_score = [var for var, score in scores.items() if score==0]
        if len(vars_zero_score)>0:
            return vars_zero_score

        return [var for var in scores.keys()]

    def pick(self, possible_vars):
        return random.choice(possible_vars)

class GTSat(Search):
    def __init__(self, name, p):
        super().__init__(name)
        self.p = p
        # p is probability of using GSAT
        # 1-p is probability of using TSAT

    def hill_climb(self, formula, assignments):
        p = self.p
        scores = formula.get_scores(assignments)

        if random.uniform(0, 1) < p:
            # use GSAT
            max_value = max(scores.values())
            items_with_max_score = [i for i in formula.variables if scores[i]==max_value]
            return items_with_max_score
        else:
            # use TSAT
            vars_positive_scores = [var for var, score in scores.items() if score>0]
            if len(vars_positive_scores)>0:
                return vars_positive_scores
            
            vars_zero_score = [var for var, score in scores.items() if score==0]
            if len(vars_zero_score)>0:
                return vars_zero_score

            return [var for var in scores.keys()]

    def pick(self, possible_vars):
        return random.choice(possible_vars)
    

def Test3CNF(searches, num_variables, num_clauses, num_tests):
    # generate 3CNF formula with num_variables and num_clauses
    # test to see if it is satisfiable
    # try it with the search algorithm
    test_results = {search_obj.name: [] for search_obj in searches}

    for i in range(num_tests):
        if i % 20== 19:
            print(i)
        # print(i)
        found_good_formula = False
        while not found_good_formula:
            cnf_formula = gen_formula(num_variables, num_clauses)
            g = Glucose3()
            for clause in cnf_formula:
                g.add_clause(clause)
            if g.solve():
                found_good_formula = True
        # print("found_good_formula")

        formula_obj = Formula(cnf_formula, "CNF")

        for search_obj in searches:
            results = search_obj.general_stochastic_local_search_CNF(formula_obj, int(9e5), 5*num_variables)
            if results is None:
                raise RuntimeError("reached max iterations")
            test_results[search_obj.name].append(results)

    return {
        search_name: {
            "average_tries": sum([result["tries"] for result in results]) / num_tests,
            "average_final_flips": sum([result["final_flips"] for result in results]) / num_tests,
            "average_total_flips": sum([result["total_flips"] for result in results]) / num_tests,
            "stdev total_flips": statistics.stdev([result["total_flips"] for result in results])
        }
        for search_name, results in test_results.items()
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
tsat_search = TSat("tsat")
gtsat_search25 = GTSat("gtsat(0.25)", 0.25)
gtsat_search50 = GTSat("gtsat(0.50)", 0.50)
gtsat_search75 = GTSat("gtsat(0.75)", 0.75)
searches = [gsat_search, tsat_search, gtsat_search25, gtsat_search50, gtsat_search75]
num_vars = 100
results = Test3CNF(searches, num_vars, int(num_vars * 4.3), 1000)

with open("results.json", "w") as f:
    json.dump(results, f)
