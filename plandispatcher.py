import utils
import bot
import linkmonitor as lm
from totalorderplan import TotalOrderPlan
import executionscript as es

# Notes on user interaction:

#   Display:
#   - current state and expected conditions.
#   - what changed.
#   - next state and new expected conditions.

#   Ask:
#   - what is different from expected state?
#   - which candidate next action is selected?

# Plan Dispatcher

class Dispatcher:
    # Given a TotalOrder Plan object,
    # performs flexible dispatching and monitoring of the plan,
    # lifted to a partial order plan.
    completed_actions = []

    def __init__(self, name: str, total_order_plan: TotalOrderPlan, trace = True):
        self.bot = bot.Bot(name, False, False)
        self.total_order_plan = total_order_plan
        self.trace = trace

        par = total_order_plan.partial_order_plan
        self.monitor = lm.CausalLinkMonitor(total_order_plan)

        # The start action has no preconditions, hence it is enabled at the beginning.
        self.enabled_actions = [par.start_action]

    def dispatch_scenario(self, scenario: es.ExecutionScenario):
        # Dispatch plan on the action observation sequence of execution_script.
        self.bot.load_scenario(scenario)
        return self.dispatch_plan()

    def dispatch_plan(self):
        # Dispatch and monitor the plan from start to finish.
        # Implements a loop of
        #      1) observe state, and check active conditions,
        #      2) select and dispatch action, and
        #      3) update active conditions and check.
        #      4) update actions to dispatch next.

        monitor = self.monitor
        b = self.bot
        successp = True
        conflicts = []
        completed = self.completed_actions

        if self.trace:
            print()
            print(f'Executing {self.total_order_plan.partial_order_plan.name}:')

        while True:
            # 1) Select the next action to dispatch and inform monitor.
            action = b.select_enabled_action(self.enabled_actions)
            if action is None:  # None if no enabled actions remain.
                break  # Terminate dispatching.
            else:
                if self.trace:
                    print()
                    print(f'   Next action {action}.')

                monitor.action_starting(action)

            # 2) perform the action.
            b.perform_action(action)

            # 3) Observe the current state, after dispatch
            #    and ask monitor to check against remaining active links.
            changes = b.observe_state_change(monitor.current_state)
            successp, conflicts = monitor.check_state_change(changes, successp, conflicts)
            if not successp:
                if self.trace:
                    print(f'      Produces conflicts {utils.list2string(conflicts)}.')

                return completed, monitor.current_state, successp, conflicts

            # 4) Ask monitor to update active links, resulting from action dispatched.
            #    Check current state against changed active links.
            successp, conflicts = monitor.check_action_dispatch(action, successp, conflicts)

            #    - Action didn't produce the intended effect, terminate dispatch.
            if not successp:
                if self.trace:
                    print(f'      Produces conflicts {utils.list2string(conflicts)}.')

                return completed, monitor.current_state, successp, conflicts

            # 5) Action produced desired effect.  Add to completed actions.
            self.completed_actions.append(action)
            completed = self.completed_actions

            #     Add newly enabled actions, resulting from dispatch .
            #     (i.e., successors of action performed, all of whose predecessors have been dispatched).
            enabled_successors = self.enabled_successors(action)

            if self.trace:
                if enabled_successors == list():
                    print(f'      Success, no enabled successors.')
                else:
                    print(f'      Success, enables successors:')
                    for sact in enabled_successors:
                        print(f'         {sact}')

            self.enabled_actions.remove(action)
            self.enabled_actions.extend(enabled_successors)

        # End: All actions dispatched.  Return with success.
        if self.trace:
                print('   Plan dispatch ended with {complete} completed.')

        return completed, monitor.current_state, successp, conflicts

    def enabled_successors(self, action):

        # Returns successors of action whose predecessors
        # have all been dispatched.
        enabled_successors = []
        for action in action.successor_actions:
            if self.action_enabledp(action) and action not in enabled_successors:
                enabled_successors.append(action)
        return enabled_successors

    def action_enabledp(self, action):
        # Returns True if all predecessors of action are completed.
        completed = self.completed_actions
        for predecessor in action.predecessor_actions:
            if predecessor not in completed:
                return False
        return True
