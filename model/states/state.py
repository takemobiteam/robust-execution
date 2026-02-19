import utils.utils as ut
import model.states.assignment as asn

# Classes that represent a state space (States and Operators):

# State is a set of assignments.

class State:
    # A state is a set of assignments that are mutable.
    # A set of assignments is encoded as a dictionary that maps
    # each variable to its variable-value assignment.
    # State can be used to represent a state at some time or a current state,
    # whose assignments change over time.

    def __init__(self, assignments: list[asn.Assignment]):
        self.assignments = dict()
        for as1 in assignments:
            var = as1.variable
            self.assignments[var] = as1

    def __str__(self):
        vals1 = list(self.assignments.values())
        str1 = ut.list2string(vals1)
        return str1

    def value(self, variable: str):
        # Given a variable of state self,
        # returns the value that variable is assigned to.
        if variable in self.assignments.keys():
            assignment: asn.Assignment = self.assignments[variable]
            return assignment.value
        else:
            return None

    def assign_value(self, variable, value):
        assignment: asn.Assignment = asn.Assignment(variable,value)
        self.assignments[variable] = assignment
