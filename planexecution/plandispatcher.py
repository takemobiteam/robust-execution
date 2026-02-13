import utils.utils as ut
import bot
import planexecution.planmonitor as lm
from plancompilation.totalorderplan import TotalOrderPlan
import planexecution.executionscenario as es

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
    # Given a TotalOrderPlan, with its lifted, partial order plan,
    # flexibly dispatch and monitor the partially ordered plan,

    completed_actions = []

    def __init__(self, name: str, total_order_plan: TotalOrderPlan, trace = True):
        self.bot = bot.Bot(name, False, False)
        self.total_order_plan = total_order_plan
        self.trace = trace

        # Get the plan to dispatch and setup the monitor for the plan.
        par = total_order_plan.partial_order_plan
        self.monitor = lm.CausalLinkMonitor(total_order_plan)

        # The start action is enabled, since it has no preconditions.
        self.enabled_actions = [par.start_action]

    def dispatch_scenario(self, scenario: es.ExecutionScenario):
        # Dispatch plan while comparing against the action and observation sequence
        # specified by scenario.
        self.bot.load_scenario(scenario)
        return self.dispatch_plan()

    def dispatch_plan(self):
        # Dispatch and monitor the plan from start to finish.
        # Implements a loop of
        #      1) observe state, and
        #         check state changes acgaints active conditions,
        #      2) select and dispatch action, and
        #      3) update active conditions and check.
        #      4) update actions to dispatch next.

        monitor = self.monitor
        b = self.bot
        successp = True # Execution is correct thus far.
        conflicts = []
        completed = self.completed_actions # Actions that have been correctly dispatched

        if self.trace:
            print()
            print(f'Executing {self.total_order_plan.partial_order_plan.name}:')

        while True:
            # 1) Select an enabled action to execute next and
            #    inform monitor that its about to be executed.
            #    Monitor removes the active causal links that action consumes.
            action = b.select_enabled_action(self.enabled_actions)
            if action is None:  # None if no enabled actions remain.
                break  # End the plan dispatch.
            else:
                if self.trace:
                    print()
                    print(f'   Next action {action}.')

                monitor.action_about_to_start(action)

            # 2) Execute the action.
            b.execute_action(action)

            # 3) Observe the state change once the action is completed
            #    and ask monitor to check this state change against the active links.
            #    - This only needs to check states changes, not the complete state.
            #    - The active links DO NOT include the links produced by action,
            #      which are handled in the next step.
            changes = b.observe_state_change(monitor.current_state)
            successp, conflicts = monitor.check_state_change(changes, successp, conflicts)
            if not successp:
                if self.trace:
                    print(f'      Produces conflicts {ut.list2string(conflicts)}.')

                return completed, monitor.current_state, successp, conflicts

            # 4) Ask monitor to update active links with the links produced by action's effects.
            #    check all assignments in the current state against the new active links.
            #    - This only checks the newly added links against state, not all links.
            successp, conflicts = monitor.check_completed_action(action, successp, conflicts)

            #    - Action didn't produce the intended effect, terminate plan dispatch
            #      and return conflicts.
            if not successp:
                if self.trace:
                    print(f'      Produces conflicts {ut.list2string(conflicts)}.')

                return completed, monitor.current_state, successp, conflicts

            # 5) Action produced the desired effect.
            # #  Recording as successfully completed actions.
            self.completed_actions.append(action)
            completed = self.completed_actions

            #     Update list of actions enabled to be dispatched,
            #     as a result of action's execution.
            #     These are successors of action, whose predecessors
            #     have all been dispatched.
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

        # Reached end of plan.  Return with success.
        if self.trace:
                print('   Plan dispatch ended with {complete} completed.')

        return completed, monitor.current_state, successp, conflicts

    def enabled_successors(self, action):
        # Returns all successor actions of action
        # whose predecessor actions
        # have all been dispatched.
        enabled_successors = []
        for action in action.successor_actions:
            if self.action_enabledp(action) and action not in enabled_successors:
                enabled_successors.append(action)
        return enabled_successors

    def action_enabledp(self, action):
        # Returns True if all predecessor actions of action have been completed.
        completed = self.completed_actions
        for predecessor in action.predecessor_actions:
            if predecessor not in completed:
                return False
        return True
