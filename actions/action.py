import utils.utils as ut
import states.assignment as asn

# An action describes elements of an operator instance:

class Action:
    # Elements of an operator instance.

    def __init__(self, operator: str, preconditions: list[asn.Assignment], effects: list[asn.Assignment]):
        self.operator = operator # a string that describes the operator instance.
        self.preconditions = preconditions # lists of assignments.
        self.effects = effects # lists of assignments.

        self.location = None  # Position of action in the totally ordered plan, starting at 0.
        self.predecessor_links = []  # Causal links with self as its consumer.
        self.predecessor_actions = []  # Producer actions that are linked self as its consumer.

        self.successor_actions = []  # Actions that immediately follow action in its partial ordered plan.
        self.successor_links = []  # Causal links with self as its producer.

    def __str__(self):
        pres = ut.list2string(self.preconditions)
        effs = ut.list2string(self.effects)
        str1 = f'{self.operator}:{pres}->{effs}'
        return str1