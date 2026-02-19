import utils.utils as ut
import model.states.state as ss
import planexecutive.executionscenario as es
import planexecutive.monitor.planmonitor as lm
import model.plans.partialorderplan as pp

# A physical (ro)Bot that mediates between the environment
# and agent (a homunculus).

# An agent asks the “bot” to
#	- observe state and report changed values,
#	- choose an enabled action to perform, and
#	- perform an action and return only when action is completed.

class Bot:

    # API for a “physical” agent that observes state,
    # chooses an enabled action and dispatches.

    def __init__(self, name: str,
                 monitor: lm.CausalLinkMonitor,
                 ask_selection: bool,
                 ask_completion: bool,
                 trace = True) -> None:
        self.name = name
        self.monitor = monitor  # Robot's plan monitor

        # If True, when an enabled action is request,
        # will ask the user to select one.
        self.ask_user_to_select_actionp:bool = ask_selection

        # If True, when an action is executed,
        # will ask the user to indicate when the action is completed.
        self.ask_user_for_action_completionp: bool = ask_completion

        # If True,
        # will print trace messages related to bot actions.
        self.trace = trace

        self.execution_scenario = None
        self.index = 0

    def __str__(self):
        return f"bot {self.name}"

    def load_scenario(self, execution_scenario: es.ExecutionScenario):
        # Load a scenario object into bot to be executed.
        self.execution_scenario = execution_scenario
        self.index = 0

    # Observe state:
    def observe_state_change(self, current_state: ss.State) -> dict:
        # Read the new state.
        # Return changed_assignments relative to current_state.
        if self.execution_scenario:
            changes = self.script_observe_state_change()
        else:
            changes = self.user_observe_state_change(current_state)

        if self.trace:
            print(f'      Observes {changes}.')

        return changes

    def script_observe_state_change(self) -> dict:
        # Extract the next observed state from the loaded execution scenario.
        current_stage = self.execution_scenario.encoded_stages[self.index]
        self.index = self.index +1
        return current_stage.state_change

    @staticmethod
    def user_observe_state_change(current_state: ss.State) -> dict:
        # Ask the user for the next observed state.
        print(f'Current state: {current_state}')
        print(f'   What changed?')
        state_change = dict()
        while True:
            variable = input("      Variable name or return for None:")
            if variable == "":
                break
            else:
                st1 = f'      Value of {variable}:'
                value = input(st1)
                state_change[variable] = value
        return state_change

    # Select an enabled action:
    def select_enabled_action(self, enabled_actions: list[ss.Action])-> ss.Action or None:
        # Select and return an enabled action, returning None if no enabled action.
        if enabled_actions == list():

            if self.trace:
                print("      No action selected.")

            return None
        elif self.execution_scenario:
            sa = self.script_select_enabled_action(enabled_actions)
        elif self.ask_user_to_select_actionp:
            sa = self.user_select_enabled_action(enabled_actions)
        else:
            # Returns first enabled action on the list.
            sa = enabled_actions[0]

        if self.trace:
            print(f'      Selects action {sa}.')

        return sa

    def script_select_enabled_action(self, enabled_actions):
        # Returns action in enabled_actions whose operator is
        # specified by the current stage of bot's execution script.
        current_stage = self.execution_scenario.encoded_stages[self.index]
        selected = current_stage.action_name
        for action in enabled_actions:
            if action.operator == selected:
                return action
        return None

    @staticmethod
    def user_select_enabled_action(enabled_actions: list[ss.Action])-> ss.Action or None:
        # Ask user to select an enabled action, returning None if no enabled action.
        while True:
            max_i: int = len(enabled_actions) - 1
            i: int = 0
            print("Choose action")
            for action in enabled_actions:
                print(f"   {i}: {action}")
                i += 1
            selected_i: int = int(input(f"Integer from 0 to {max_i}:"))
            if ut.index_in_rangep(selected_i, 0, max_i):
                break
            else:
                print(f"{selected_i} not an index in [0, {max_i}].")
        return enabled_actions[int(selected_i)]

    # Execute action:
    def execute_action(self, action: ss.Action, successp: bool, conflicts: list[pp.LinkConflict]):
        # Tell bot to perform action, optionally waiting to confirm completion.
        # Checks that action does not violate causal links that are active during execution.
        # (but does not confirm effects).
        # ToDo Document returned values in this and similar methods.
        if self.ask_user_for_action_completionp:
            input(f"{self }: Perform {action.operator} and hit return.")
        else:
            print(f"      Dispatches {action.operator}.")

        # Observe state changes after the action completes.
        changes = self.observe_state_change(self.monitor.current_state)
        # Ask monitor to check the resulting state change against the active links.
        # - This only needs to check states changes, not the complete state.
        # - The active links DO NOT include the links produced by action,
        #   which are handled in the next step.
        successp, conflicts = self.monitor.check_state_change(changes, successp, conflicts)

        return successp, conflicts