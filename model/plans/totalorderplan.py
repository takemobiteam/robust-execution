import model.actions.action as am
import model.states.assignment as asn
import plancompiler.extractpartialorderplan as ex
import utils.utils as ut

# Total Order Plan:

class TotalOrderPlan:
    # Class that represents a total order plan, its encoding, and its corresponding partial order plan.
    # Total order plan is composed of an action sequence, start and goal assignments.
    # Objects representing total order plan encoding and
    # partial order plan compilation are generated automatically.
    # - The total order plan is encoded by introducing the start and goal as start and end actions.
    # - Its partial order plan is the set of plan actions, causal links that close preconditions,
    #   and orderings that are needed to resolve threats.

    def __init__(self, name: str, action_sequence: list[am.Action], start : list[asn.Assignment], goal: list[asn.Assignment]):
        # Record the plan, encode it and extract its least commitment plan.
        self.name = name
        self.action_sequence = action_sequence
        self.start = start
        self.goal = goal
        encoding = encode_total_order_plan(action_sequence, start, goal)
        self.encoded_sequence = encoding
        pop_plan, threats = ex.extract_partial_order_plan(self.name, self.encoded_sequence)
        self.partial_order_plan = pop_plan
        self.threats = threats
        if threats:
            actstr = ut.list2string(self.action_sequence)
            print(f"In plan {self}: {actstr}:")
            for threat in self.threats:
                print(f"  Link {threat.link} is threatened by action {threat.action}.")

    def __str__(self):
        return f"TOP {self.name}"

    def display(self):
        # Print start, goal and action sequence.
        print(f'{self}:')
        print(f'   Start: {ut.list2string(self.start)}')
        print(f'   Goal: {ut.list2string(self.goal)}')
        print('   Sequence:')
        for act in self.action_sequence:
            print(f'      {act}')

    def display_all(self):
        # print total order plan, its encoding and its partial order plan,
        self.display()
        print()
        self.display_encoding()
        print()
        self.display_pop()

    def display_encoding(self):
        # Print the encoded action sequence.
        print(f'Encoding of {self}:')
        for act in self.encoded_sequence:
            print(f'      {act}')

    def display_pop(self):
        # Print the partial order plan extracted from action sequence.
       self.partial_order_plan.display()

# Encode a total order plan (start, goal and action sequence):

def encode_total_order_plan(action_sequence: list[am.Action], start: list[asn.Assignment], goal: list[asn.Assignment]) -> list[am.Action]:
    # Adds to plan (action_sequence) its start and goal states as actions,
    # and records the location of each action.
    # Returns the encoded sequence.

    encoded_sequence = action_sequence[:]
    start_action = am.Action("start", [], start)
    encoded_sequence.insert(0, start_action)    # Add start action to the
                                                # beginning of the plan.
    goal_action = am.Action("goal", goal, [])
    encoded_sequence.append(goal_action)	    # Add goal action to the
                                                # end of the plan.
    add_location_to_actions(encoded_sequence)   # Associate with each action its
    # position in the sequence.

    return encoded_sequence

def add_location_to_actions(encoded_sequence: list[am.Action]):
    # For each action in the total order plan, record its position.
    # Method called for effect only.
    i: int = 0
    for action in encoded_sequence:
        action.location = i
        i += 1
