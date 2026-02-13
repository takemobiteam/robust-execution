import utils

# Classes that define State spaces (States and Operators):

# State is a set of assignments.

class Assignment:
    # A variable / value assignment.
    def __init__(self, variable: str, value):
        self.variable = variable
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Assignment) and self.__dict__ == other.__dict__

    def __str__(self):
        return f"{self.variable}={self.value}"

class State:
    # A state is a set of assignments that are mutable.
    # A set of assignments is encoded as a dictionary that maps
    # each variable to its variable-value assignment.
    # State can be used to represent a state at some time or a current state,
    # whose assignments change over time.

    def __init__(self, assignments: list[Assignment]):
        self.assignments = dict()
        for as1 in assignments:
            var = as1.variable
            self.assignments[var] = as1

    def __str__(self):
        vals1 = list(self.assignments.values())
        str1 = utils.list2string(vals1)
        return str1

    def value(self, variable: str):
        # Given a variable of self state, returns the value that variable is bound to.
        if variable in self.assignments.keys():
            assignment: Assignment = self.assignments[variable]
            return assignment.value
        else:
            return None

    def assign_value(self, variable, value):
        assignment: Assignment = Assignment(variable,value)
        self.assignments[variable] = assignment

# An operator is an action:

class Action:
    # An operator instance.

    def __init__(self, operator: str, preconditions: list[Assignment], effects: list[Assignment]):
        # operator is a string.  Preconditions and effects are lists of assignments.
        self.operator = operator
        self.preconditions = preconditions
        self.effects = effects

        self.location = None  # Position of action in the totally ordered plan, starting at 0.
        self.predecessor_links = []  # links with self as its consumer.
        self.predecessor_actions = []  # preceding actions that are linked

        self.successor_actions = []  # Actions that immediately follow action in its partial ordered plan.
        self.successor_links = []  # links with self as its producer.

    def __str__(self):
        pres = utils.list2string(self.preconditions)
        effs = utils.list2string(self.effects)
        str1 = f'{self.operator}:{pres}->{effs}'
        return str1