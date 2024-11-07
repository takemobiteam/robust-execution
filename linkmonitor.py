import statespace as ss
import partialorderplan as pp

# Causal Link Monitor:

class CausalLinkMonitor:
    # Monitors the (causal) links of a plan as state is observed over time.
    # Current state starts with start_assignments.

    def __init__(self, total_order_plan, trace = True):
        p = total_order_plan.partial_order_plan
        self.trace = trace
        self.links = p.links
        self.active_links = []

        # Encode the current_state as a mutable object.
        self.current_state = ss.State([])

    def current_value(self, variable: str):
        # Returns the assignment for variable in the current state.
        self.current_state.value(variable)

    def assign_current_value(self, variable: str, value: str):
        # Updates the assignment for variable in the current state to have value.
        self.current_state.assign_value(variable, value)

    def update_state(self, changed_assignments: dict):
        # Updates the current state of monitor with changed assignments.
		# changed_assignments is a set of assignments.
        # Called for effect.
        for variable, value in changed_assignments.items():
            self.assign_current_value(variable, value)

    def check_state_change(self, changed_assignments: dict, successp: bool, conflicts: list[pp.LinkConflict]):
        # Checks if any assignment in changed_assignments
        # violates an active link.

        if self.active_links == list():
            if self.trace:
                print(f'         No past active links to check.')

        else:
            if self.trace:
                print(f'         Checking past active links')

            for variable, value in changed_assignments.items():

                for link in self.active_links:
                    successp, conflicts = self.check_w_obs(link, variable, value, successp, conflicts)

                    if self.trace:
                        if successp:
                            print(f'            Satisfies link {link}.')
                        else:
                            print(f'            Violates link {link}.')

        return successp, conflicts

    def action_starting(self, action: ss.Action):
        # Tells monitor that action is being dispatched.
        # Monitor removes the active causal links that have been consumed.

        # Deactivate active links that action consumes.
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

    def check_action_dispatch(self, action: ss.Action, successp: bool, conflicts: list[pp.LinkConflict]):
        # Tells monitor that action dispatched and asks to check effects.
        # Monitor activates causal links produced by action, and
        # checks newly active links against current state, observed since dispatch.

        # Activate links that action produces, while checking against current state.
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

            for link in slinks:
                self.active_links.append(link)
                successp, conflicts = self.check_w_state(link, successp, conflicts)

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

    def check_w_state(self, link: pp.CausalLink, successp: bool, conflicts: list[pp.LinkConflict]):
        # Check that the state agrees with the condition of the link.
        state = self.current_state

 #       print(f'Checking link {link}. against {state}')

        condition = link.condition
        cvar = condition.variable
        cval = condition.value
        oval = state.value(cvar)
        if oval is not None and oval != cval:
            # Record conflict when state violates the link’s condition.
            successp = False
            conflict = pp.LinkConflict(link, oval)
            conflicts.append(conflict)
        return successp, conflicts

    @staticmethod
    def check_w_obs(link: pp.CausalLink, variable: str, value: str, successp: bool, conflicts: list[pp.LinkConflict]):
        # Check that assignment obs agrees with the condition of the link.
        cond = link.condition
        cvar = cond.variable

        # obs disagrees with the condition of link
        # if they assign different values to the same variable.
        if variable == cvar and value != cond.value:
            successp = False
            conflicts.append(pp.LinkConflict(link, value))
        return successp, conflicts
