import json
from pathlib import Path
import model.states.state as ss
import model.plans.totalorderplan as tp
import planexecutive.executionscenario as es
import planexecutive.dispatcher.plandispatcher as pd

# The plan library reads total order plan and execution scenario descriptions,
# creates corresponding TotalOrderPlan and ExecutionScenario objects,
# and records them in a library for retrieval.

# Plan Input Format:

#    <grounded_plan> ::= “{“ “plan_name” “:” <string_name> “,”
#                                “start” “:” <assignments> “,”
#                                 “goal” “:” {<assignments>,
#                             “sequence” “:” <action_sequence> "}"

#      <assignments> ::= “{“ <assign> ("," <assign>)*  “}”

#           <assign> ::= <var> “:” <val>

#  <action_sequence> ::= “[“ <action> ("," <action>)* “]”

#           <action> ::= “{“         “name” ":" <action_name> “,”
#                            “precondition” “:” <assignments> “,”
#                                  “effect” “:” <assignments> “}”

#      <action_name> ::= <string>


# Scenario Input Format:

#        <scenario>  ::= “{“ “scenario_name” “:” <string_name> “,”
#                                “plan_name” “:” <string_name> “,”
#                                    “start” “:” <assignments> “,”
#                                “execution” “:” <stage_seq> "}"

#        <stage_seq> ::= "[]" |
#                        "[" <stage> ("," <stage>)* "]"

#            <stage> ::= "{" “action” : <action_name> “,” “state_change” : <assignments> "}"

#           Note: if [], then execution supplied by user.


# Scenario Output Format:

#       <scenario_output> ::= “{“        “partial_plan” “:” <partial_order_plan> “,”
#                                 “monitored_execution” “:” <monitored_execution> "}"

#  <partial_order_plan> ::= “{" “actions” “:” <actions> “,”
#                                 “links” “:” <links> “,”
#                             “orderings” “:” <orderings> “}”

#             <actions> ::= “{" <action> ("," <action>)* “}”

#               <links> ::= “{"  <link> ("," <link>)* “}”

#                <link> ::= {“condition” “:” <assign> “,”
#                             “producer” “:” <action_name> “,”
#                             “consumer” “:” <action_name> “}”

#           <orderings> ::= “{"  <ordering> ("," <ordering>)* “}”

#            <ordering> ::= "{" “predecessor” “:” <action_name> “,”
#                                 “successor” “:” <action_name> “}”

# <monitored_execution> ::= "["
#                                "{" “start” : <assignments> "}"
#                               ("{" “action” : <action_name> “,”
#                                    “activated_conditions” : <assignments> “,”
#                                    “deactivated-conditions” : <assignments> “,”
#                                    “state-change” : <assignments> "}")*
#                           "]"

# Example Scenario Input 1:

#      """{
#            "plan_name" : "Plan1",
#            "plan" :
#                {
#                    "start" : {"P" : "True", "Q" : "True"},
#                    "goal" : {"P" : "False"},
#                    "sequence":
#                        [
#                            {"action" : "A1", "precondition" : {"P" : "True", "Q" : "True"}, "effect" : {"Q" : "False"}},
#                            {"action" : "A2", "precondition" :  {"Q" : "False"}, "effect" :  {"P" : "False"}}
#                        ]
#                },
#
#            "execution" :
#                {
#                    "start" : {"P" : "True", "Q" : "True"},
#                    "sequence":
#                        [
#                            {"action" : "A1" , "state_change" : {"Q" : "False"}},
#                            {"action" : "A2" , "state_change" : {"P" : "False"}}
#                        ]
#                },
#                [

#                ]
#        }"""

# Example Scenario Input 2:

#      """{
#            "plan_name" : "Rescue",
#            "plan" :
#                {
#                    "start" : {"bay_empty" : "True", "in_air" : "False"},
#                    "goal" : {"hikers_w_medkit" : "True"},
#                    "sequence":
#                        [
#                            {"action" : "launch",
#                               "precondition" :  {"in_air" : "False"},
#                               "effect" :  {"in_air" : "True"}}
#                            {"action" : "fly_to_base",
#                               "precondition" :  {"in_air" : "True"},
#                               "effect" :  {"near_medkit" : "True"}}
#                            {"action" : "pick_up_medkit",
#                               "precondition" :  {"near_medkit" : "True", bay_empty: "True"},
#                               "effect" :  {"has_medkit" : "True", bay_empty: "False"}}
#                            {"action" : "fly_to_hikers",
#                               "precondition" :  {"in_air" : "True"},
#                               "effect" :  {"near_hikers" : "True"}}
#                            {"action" : "drop_medkit",
#                               "precondition" :  {"has_medkit" : "True", "near_hikers" : "True"},
#                               "effect" :  {"hikers_w_medkit" : "True"}}
#                        ]
#                },
#
#            "execution" :
#                {
#                    "start" : {"bay_empty" : "True", "in_air" : "False", "has_medkit" : "False"},
#                    "sequence":
#                        [
#                            {"action" : "launch" ,
#                               "state_change" : {"in_air" : "True"}},
#                            {"action" : "fly_to_base" ,
#                               "state_change" : {"near_medkit" : "True"}}
#                            {"action" : "pick_up_medkit",
#                               "state_change" : {"has_medkit" : "True", bay_empty: "False"}}
#                            {"action" : "fly_to_hikers" ,
#                               "state_change" : {"near_hikers" : "True"}}
#                            {"action" : "drop_medkit" ,
#                               "state_change" : {"hikers_w_medkit" : "True"}}
#                        ]
#                }
#        }"""

# ***  Scenarios ***

class PlanLibrary:
    def __init__(self, scenario_directory_name = "", trace = True):
       # Set the directory containing scenarios.
       # If no directory specified, default to the current working directory.
        if scenario_directory_name == "":
            self.scenario_directory_name = Path.cwd()
        else:
            self.scenario_directory_name = scenario_directory_name

        self.scenario_directory = Path(self.scenario_directory_name)

        print(f"Will look for scenarios in directory {self.scenario_directory}.")

        self.trace = trace

        # Libraries of plan compilation and execution scenarios that have been read in.
        self.plan_library = dict()
        self.scenario_library = dict()

    # Read plans into Library

    def readplan(self, plan_relative_path : str) -> tp.TotalOrderPlan:
        # Creates a python plan object and registers in plan library.
        # relative_path_for_plan points to a file containing a json plan description.
        fn = self.scenario_directory / plan_relative_path

        if fn.exists():
            with open(fn, "rt") as file:
                json_plan = file.read()
                return self.json2plan(json_plan)
        else:
            print(f"File {fn} does not exist in {self.scenario_directory}.")

    def json2plan(self, json_plan) -> tp.TotalOrderPlan:
        # Converts a json description of a total order plan,
        # json_plan, to a python total order plan object.
        dict_plan = json.loads(json_plan)
        return self.dict2plan(dict_plan)

    def dict2plan (self, dict_plan) -> tp.TotalOrderPlan:
        # Converts a dictionary description of a total order plan,
        # dict_plan, to a python total order plan object.
        plan_name, plan = dict2total_order_plan(dict_plan)

        # Register plan in DispatcherIO's plan library.
        self.plan_library[plan_name] = plan
        if self.trace:
            print(f"Adding plan {plan_name} to library as {plan}.")
        return plan

    def get_plan (self, plan_name: str) -> tp.TotalOrderPlan or None:
        # Retrieves plan from the library.
        return  self.plan_library.get(plan_name)


    # Read Execution Scenario into Library

    def readscenario(self, relative_path_for_scenario : str) -> es.ExecutionScenario:
        # Creates a scenario dictionary, containing a plan name and a plan execution,
        # which corresponds to a json plan execution scenario description,
        # at the file pointed to by relative_path_for_scenario.
        fn = self.scenario_directory / relative_path_for_scenario
        if Path.exists(fn):
            with open(fn, "rt") as file:
                json_scenario = file.read()
                return self.json2scenario(json_scenario)
        else:
            print(f"File {fn} does not exist in {self.scenario_directory}.")

    def json2scenario(self, json_scenario)-> es.ExecutionScenario:
        # Converts a json description of a plan execution scenario,
        # json_scenario, to a dictionary, containing a plan name and a plan execution.
        dict_scenario = json.loads(json_scenario)
        return self.dict2scenario(dict_scenario)

    def dict2scenario (self, dict_scenario) -> es.ExecutionScenario:
        # Converts a dictionary description of a scenario,
        # dict_scenario, to a dictionary that contains a plan name and a python execution object.
        scenario_name: str = dict_scenario["scenario_name"]
        plan_name: str = dict_scenario["plan_name"]
        start = dict_scenario["start"]
        seq = dict2stage_sequence(dict_scenario["sequence"])

        scenario: es.ExecutionScenario = es.ExecutionScenario(scenario_name, plan_name, start, seq)

        self.scenario_library[scenario_name] = scenario

        if self.trace:
            print(f"Adding scenario {scenario_name} to library as {scenario}.")

        plan = self.get_plan(plan_name)
        if plan is None:
            print(f"Scenario {scenario_name} is for plan {plan_name}, which is not yet in the Library.")

        return scenario

    def get_scenario (self, scenario_name: str) -> es.ExecutionScenario or None:
        return  self.scenario_library.get(scenario_name)


    # Execute Library Scenario using the Dispatcher

    def dispatch_scenario(self, scenario_name):
        # Dispatch library execution scenario named scenario_name.

        scenario = self.get_scenario(scenario_name)
        if scenario is None:
            print(f"Can't dispatch scenario {scenario_name}.  Not in the Library.")
        else:
            plan_name = scenario.plan_name
            plan = self.get_plan(plan_name)
            if plan is None:
                print(f"Can't dispatch scenario {scenario_name}, its plan {plan_name} isn't in the Library.")
            else:
                disp1 = pd.Dispatcher(f'Dispatcher for {plan_name}', plan)
                completed, end_state, successp, conflicts = disp1.dispatch_scenario(scenario)

                print_scenario_results(scenario_name, plan_name, end_state, successp, completed, conflicts)

def print_scenario_results(scenario_name: str, plan_name: str, end_state, successp: bool, completed, conflicts):
    print()
    print(f"Scenario {scenario_name} for {plan_name} ended:")
    if successp:
        print(f"   Scenario succeeded.")
    else:
        print(f"   Scenario failed.")

    print(f"   End state: {end_state}")

    print("   completed actions:")
    for act1 in completed:
        print(f"      {act1}")

    if not successp:
        print(f"   conflicts:")
    for c1 in conflicts:
        print(f"      {c1}")


# ***  Creating Total Order plans ***

def dict2total_order_plan (dict_plan)-> (str, tp.TotalOrderPlan):
    # Converts a dictionary description of a total order plan,
    # dict_plan, to a python total order plan object.
    plan_name: str = dict_plan["plan_name"]
    start = dict2assignments(dict_plan["start"])
    goal = dict2assignments(dict_plan["goal"])
    sequence = dict2plan_sequence(dict_plan["sequence"])
    plan = tp.TotalOrderPlan(plan_name, sequence, start, goal)
    return plan_name, plan

def dict2assignments (dict_assignments):
    # Converts a dictionary description of a set of assignments,
    # dict_assignments, to a python assignments object.
    asgns = list()
    for var, val in dict_assignments.items():
        asgn = ss.Assignment(var, val)
        asgns.append(asgn)
    return asgns

def dict2plan_sequence (dict_sequence):
    # Converts a dictionary description of an action sequence,
    # dict_sequence, to a list of python action objects.
    pseq = list()
    for dict_action in dict_sequence:
        action = dict2action(dict_action)
        pseq.append(action)
    return pseq
    
def dict2action (dict_action)->ss.Action:
    # Converts a dictionary description of an action,
    # dict_action, to a python action object.
    action_name: str = dict_action["action"]
    pre = dict2assignments(dict_action["precondition"])
    eff = dict2assignments(dict_action["effect"])
    return ss.Action(action_name, pre, eff)


# ***  Creating Plan Execution Sequences ***

def dict2stage_sequence (dict_stage_sequence)-> list[es.Stage]:
    # Converts a dictionary description of an execution sequence,
    # dict_stage_sequence, to a list of python stage object.
    pseq = list()
    for dict_stage in dict_stage_sequence:
        stage = dict2stage(dict_stage)
        pseq.append(stage)
    return pseq

def dict2stage (dict_stage)-> es.Stage:
    # Converts a dictionary description of an execution stage,
    # dict_stage, to a python stage object.
    action_name = dict_stage["action"]
    state_change = dict_stage["state_change"]
    return es.Stage(action_name, state_change)
