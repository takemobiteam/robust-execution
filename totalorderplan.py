import statespace as ss
import extractpop as ex
import utils

# Total Order Plan:

class TotalOrderPlan:
    # Class that represents a total order plan, its encoding, and its corresponding partial order plan.
    # Total order plan is composed of an action sequence, start and goal assignments.
    # Encoding and partial order plans are generated automatically.
    # - The total order plan is encoded by introducing the start and goal as start and end actions.
    # - Its partial order plan is the set of plan actions, plus causal links that close preconditions,
    #   and orderings needed to resolve threats.

    def __init__(self, name: str, action_sequence: list[ss.Action], start : list[ss.Assignment], goal: list[ss.Assignment]):
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
            actstr = utils.list2string(self.action_sequence)
            print(f"In plan {self}: {actstr}:")
            for threat in self.threats:
                print(f"  Link {threat.link} is threatened by action {threat.action}.")

    def __str__(self):
        return f"TOP {self.name}"

    def display(self):
        # Print start, goal and action sequence.
        print(f'{self}:')
        print(f'   Start: {utils.list2string(self.start)}')
        print(f'   Goal: {utils.list2string(self.goal)}')
        print('   Sequence:')
        for act in self.action_sequence:
            print(f'      {act}')

    def display_all(self):
        self.display()
        self.display_encoding()
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

def encode_total_order_plan(action_sequence: list[ss.Action], start: list[ss.Assignment], goal: list[ss.Assignment]) -> list[ss.Action]:
    # Add to plan (action_sequence) its start and goal as actions,
    # and records the location of each action.
    # Start and end operators add to start and end of the plan.
    # Returns the encoded sequence.

    encoded_sequence = action_sequence[:]
    start_action = ss.Action("start", [], start)
    encoded_sequence.insert(0, start_action)    # Add start action to the
                                                # beginning of the plan.
    goal_action = ss.Action("goal", goal, [])
    encoded_sequence.append(goal_action)	    # Add goal action to the
                                                # end of the plan.
    add_location_to_actions(encoded_sequence)   # associate with each action its location.

    return encoded_sequence

def add_location_to_actions(encoded_sequence: list[ss.Action]):
    # For each action in the total order plan, record its position.
    # Called for effect only.
    i: int = 0
    for action in encoded_sequence:
        action.location = i
        i += 1
