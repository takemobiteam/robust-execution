import model.actions.action as am
import planexecutive.stateestimator.currentstate as cs
import model.plans.partialorderplan as pp

# Causal Link Monitor:

class CausalLinkMonitor:
    # Monitors the (causal) links of a plan as state is observed over time.
    # Current state starts with start_assignments.

    def __init__(self, total_order_plan, trace = True):
        self.trace = trace  # Should we trace monitoring?
        p = total_order_plan.partial_order_plan
        self.links = p.links # All links to be monitored.
        self.active_links = [] # No active links until start action dispatched.

        # Encode the current_state as a mutable object.
        self.current_state = cs.CurrentState([],self.trace)

    # Check a state change against all active links.

    def check_state_change(self, changed_assignments: dict, successp: bool, conflicts: list[pp.LinkConflict]):
        # Checks if any assignment in changed_assignments
        # violates one of the active links.

        if self.active_links == list():
            if self.trace:
                print(f'         No past active links to check.')

        else:
            if self.trace:
                print(f'         Checking past active links')

            for variable, value in changed_assignments.items():

                # Check changed variable assignment against all active links.
                for link in self.active_links:
                    successp, conflicts = self.check_link_against_variable_assignment(link, variable, value, successp, conflicts)

                    if self.trace:
                        if successp:
                            print(f'            Satisfies link {link}.')
                        else:
                            print(f'            Violates link {link}.')

        return successp, conflicts

# Update monitor for action that is about to be invoked.
# - Disable links consumed by action.

    def monitor_action_start(self, action: am.Action):
        # Tells monitor that action just started.
        # Monitor removes the active causal links that action consumes.

        # Deactivates active links that action consumes.
        rlks = []
        for link in self.active_links:
            if action == link.consumer:
                # print(f'      {action} consumes link {link}.')
                rlks.append(link)
            # else:
            #    print(f'      {action} does not consume link {link}.')

        if self.trace:
            if rlks == list():
                print(f'      No links consumed.')
            else:
                print(f'      Links consumed:')
                for rlk in rlks:
                    self.active_links.remove(rlk)
                    print(f'         {rlk}.')

    # Update monitor for completed action.
    # - Enable links produced by action.
    #  - Check new links against state.

    def monitor_completed_action(self, action: am.Action, successp: bool, conflicts: list[pp.LinkConflict]):
        # Tells monitor that action was just completed and asks to check effects.
        # Monitor activates causal links produced by action, and
        # checks the produced links against the current state.
        # Assume:
        # - Action was just completed.
        # - State was observed and updated since action produced its effects.

        # Activate each link that action produces.
        slinks = action.successor_links
        if slinks == list():
            if self.trace:
                print(f'      Action activates no links.')
        else:
            if self.trace:
                print(f'      Action activates links:')
                for slink in slinks:
                    print(f'         {slink}:')
                print(f'      Check new links against state:')

            # Check each link produced against the current state.
            for link in slinks:
                self.active_links.append(link)
                successp, conflicts = self.check_link_against_state(link, successp, conflicts)

                if self.trace:
                    if successp:
                        print(f'         State satisfies link {link}.')
                    else:
                        print(f'         State violates link {link}.')

        if self.active_links == list():
            print(f'      No links currently active.')
        else:
            print(f'      Current active links:')
            for link in self.active_links:
                 print(f'         {link}')

        return successp, conflicts

    def check_link_against_state(self, link: pp.CausalLink, satisfiedp: bool, conflicts: list[pp.LinkConflict]):
        # Check the condition of link against the current state.
        # Assumes the current state is up to date.
        # Updates satisfiedp and conflicts if link is violated.
        # A conflict is a violated link plus the state value that violates the condition.
        state = self.current_state

 #       print(f'Checking link {link}. against {state}')

        condition = link.condition
        cvar = condition.variable
        cval = condition.value
        oval = state.value(cvar)
        if oval is not None and oval != cval:
            # Record conflict when state violates the link’s condition.
            satisfiedp = False
            conflict = pp.LinkConflict(link, oval)
            conflicts.append(conflict)
        return satisfiedp, conflicts

    @staticmethod
    def check_link_against_variable_assignment(link: pp.CausalLink, variable: str, value: str, successp: bool, conflicts: list[pp.LinkConflict]):
        # Check that the observed assignment (variable value)
        # agrees with the condition of link.
        cond = link.condition
        cvar = cond.variable

        # obs disagrees with the condition of link
        # if they assign different values to the same variable.
        if variable == cvar and value != cond.value:
            successp = False
            conflicts.append(pp.LinkConflict(link, value))
        return successp, conflicts
