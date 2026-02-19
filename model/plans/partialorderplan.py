import model.actions.action as am
import model.states.assignment as asn
import typing

# Partial Order plans

class CausalLink:
    # Describes the actions that produce and rely upon a condition.
    def __init__(self, condition: asn.Assignment, producer: am.Action or None, consumer: am.Action):
        self.condition = condition  # An assignment
        self.producer = producer  # Action with an effect that is condition.
        self.consumer = consumer  # Action with a precondition that is condition.

    def __str__(self):
        return f"{self.condition}: {self.producer}->{self.consumer}"

class LinkConflict:
    # Conflict between an activated causal link and an observed value.
    def __init__(self, link: CausalLink, observed_value: typing.Any):
        self.link = link  # The active causal link that was violated.
        self.observed_value = observed_value  # Observed value that violates
        # causal link’s condition.

    def __str__(self):
        return f"{self.observed_value} violates active {self.link})"

class Ordering:
    # Specifies a partial order between actions in a plan.
    def __init__(self, predecessor: am.Action, successor: am.Action):
        self.predecessor = predecessor  # Action that occurs first.
        self.successor = successor  # Action that occurs later.

    def __str__(self):
        return f"{self.predecessor} < {self.successor})"

class Threat:
    # Specifies the threat of an action to a causal link.
    def __init__(self, causal_link: CausalLink, action: am.Action):
        self.link = causal_link  # Causal link whose condition is threatened.
        self.action = action  # Action that threatens the link.

    def __str__(self):
        return f"{self.action} threatens {self.link})"

# Partial order plan and its elements:

class PartialOrderPlan:
    # Class representing a partial order plan, comprised of a set of actions,
    # causal links between actions, representing producers and consumers of conditions,
    # and partial orders between actions, needed to resolve threats.
    # Start and goal assignments are encoded as two operators.

    def __init__(self, name: str, actions: list[am.Action], links: list[CausalLink], orderings: list[Ordering],
                 start_action: am.Action):
        # operator is a symbol, preconditions and effects are sets of assignments.
        self.name = name
        self.actions = actions  # Set of all operator instantiations of plan.
        self.links = links  # Set of causal links between actions.
        self.orderings = orderings  # Set of partial orders between actions.
        self.start_action = start_action  # The first action that is invoked in the plan.
        # This is the action that produces the start state.

    def __str__(self):
        return f"POP {self.name}"

    def display(self):

        print(f'{self}:')

        print('   Actions:')
        for act in self.actions:
            print(f'      {act}')

        print('   Causal links:')
        for lnk in self.links:
            print(f'      {lnk}')

        print('   Orderings:')
        if self.orderings == list():
            print('      none')
        else:
            for or1 in self.orderings:
                print(f'      {or1}')