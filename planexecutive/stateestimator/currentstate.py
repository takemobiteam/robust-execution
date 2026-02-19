import model.states.state as st
import model.states.assignment as asn

class CurrentState(st.State):

    def __init__(self, assignments: list[asn.Assignment], trace = True):
        self.trace = trace
        st.State.__init__(self, assignments)

    #  Update the record of the current state

    def current_value(self, variable: str):
        # Returns the assignment to variable in the current state.
        self.value(variable)

    def assign_current_value(self, variable: str, value: str):
        # Updates the assignment to variable in the current state to be value.
        self.assign_value(variable, value)

    def update_state(self, changed_assignments: dict):
        # Updates the current state with changed_assignments.
        # changed_assignments is a set of variable assignments.
        # Called for effect.
        if self.trace:
            print(f'         Updating state:')
        for variable, value in changed_assignments.items():
            if self.trace:
                print(f'           {variable} = {value}')
            self.assign_current_value(variable, value)