# Plan Execution Script

class Stage:
    # One step in a plan execution.

    def __init__(self, action_name: str, state_change: dict):
        # action_name is a string.  state_change is a list of assignments.
        self.action_name = action_name
        self.state_change = state_change

    def __str__(self):
        return f'{self.action_name}->{self.state_change}'

class ExecutionScenario:
    # An execution scenario of plan named plan_name, as the sequence of observed states and actions invoked.
    # Described an observed initial state, followed by invoked action / observe state change pairs (called stages).

    # The user is requested to provide online input for a test if no stages are provided.

    def __init__(self, scenario_name, plan_name: str, start: dict, stages: list[Stage]):
        # action_name is a string. state_change is a list of assignments.
        self.scenario_name = scenario_name
        self.plan_name = plan_name
        self.start = start
        self.stages = stages
        start_stage = Stage("start", self.start)
        goal_stage = Stage("goal", dict())
        self.encoded_stages = self.stages[:]
        self.encoded_stages.insert(0,start_stage)
        self.encoded_stages.append(goal_stage)

    def __str__(self):
        return f'Scenario {self.scenario_name}'

    def display_execution(self):
        print(f'{self.scenario_name} -executing {self.plan_name}:')

        if self.stages == list():
            print("   User guided.")
        else:
            print(f'   {self.start}')
            for stg in self.stages:
                print(f'   {stg}')