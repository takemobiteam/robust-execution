# Project RobustExecution

# Test of loading plans and scenarios from files.

# To run this scratch file from any project:
import sys
sys.path.insert(0,'/Users/brian/PycharmProjects/robustExecution/robust-execution')

#import bot
import planlibrary as plib
import json

print('This scratch file exercises basic routines of PlanLibrary for File IO.')

print()

t1 = """{
             "plan_name" : "plan_1",
             "plan" :
                {
                    "start" : {"P" : "True", "Q" : "True"},
                    "goal" : {"P" : "False"},
                    "sequence":
                        [
                            {"action" : "A1", "precondition" : {"P" : "True", "Q" : "True"}, "effect" : {"Q" : "False"}},
                            {"action" : "A2", "precondition" :  {"Q" : "False"}, "effect" :  {"P" : "False"}}
                        ]
                },
            "execution" :
                {
                    "start" : {"P" : "True", "Q" : "True"},

                    "sequence" :
                        [
                            {"action" : "A1" , "state_change" : {"Q" : "False"}},
                            {"action" : "A2" , "state_change" : {"P" : "False"}}
                        ]
                }
        }"""

tp1 = """{
                "plan_name" : "plan_1",
                "start" : {"P" : "True", "Q" : "True"},
                "goal" : {"P" : "False"},
                "sequence":
                        [
                            {"action" : "A1", "precondition" : {"P" : "True", "Q" : "True"}, "effect" : {"Q" : "False"}},
                            {"action" : "A2", "precondition" :  {"Q" : "False"}, "effect" :  {"P" : "False"}}
                        ]
        }"""

print(tp1)

lp1 = json.loads(tp1)
print(lp1)

print(lp1["plan_name"])
print(lp1["start"])
print(lp1["goal"])
print(lp1["sequence"])

op1 = json.dumps(lp1, indent=4)

print(op1)

te1 = """{
            "scenario_name" : "scenario_1",
            "plan_name" : "plan_1",
            "start" : {"P" : "True", "Q" : "True"},
            "sequence" :
                        [
                            {"action" : "A1" , "state_change" : {"Q" : "False"}},
                            {"action" : "A2" , "state_change" : {"P" : "False"}}
                        ]
        }"""

le1 = json.loads(te1)
print(lp1)

print(le1["scenario_name"])
print(le1["plan_name"])
print(le1["start"])
print(le1["sequence"])

oe1 = json.dumps(le1, indent=4)

print(oe1)

# mylib = plib.PlanLibrary("~/PycharmProjects/robustExecution/examples/")
mylib = plib.PlanLibrary("/Users/brian/PycharmProjects/robustExecution/examples/")

# pp1 = mylib.dict2plan(lp1)
pp1 = mylib.readplan("hello_plan.txt")

print(pp1)

pe1 = mylib.dict2scenario(le1)
print(pe1)

pp1.display()
pp1.display_encoding()
pp1.display_pop()
pp1.display_all()

pe1.display_execution()

mylib.dispatch_scenario("Scenario1")

print("Test 2 begins:")

t2 = """{
            "plan_name" : "Rescue",
            "plan" :
                {
                    "start" : {"bay_empty" : "True", "in_air" : "False"},
                    "goal" : {"hikers_w_medkit" : "True"},
                    "sequence":
                        [{"action" : "launch", 
                            "precondition" : {"in_air" : "False"}, 
                            "effect" : {"in_air" : "True"}},
                         {"action" : "fly_to_medkit", 
                            "precondition" : {"in_air" : "True"}, 
                            "effect" : {"near_medkit" : "True"}},
                         {"action" : "pickup_medkit",
                            "precondition" :  {"near_medkit" : "True", "bay_empty" : "True"},
                            "effect" :  {"has_medkit" : "True", "bay_empty" : "False"}},
                         {"action" : "fly_to_hikers",
                            "precondition" :  {"in_air" : "True"},
                            "effect" :  {"near_hikers" : "True"}},
                         {"action" : "drop_medkit",
                            "precondition" :  {"has_medkit" : "True", "near_hikers" : "True"},
                            "effect" : {"hikers_w_medkit" : "True"}}
                        ]
                },
            "execution" :
                {
                    "start" : {"bay_empty" : "True", "in_air" : "False", "has_medkit" : "False"},
                    "sequence":
                        [
                            {"action" : "launch",
                               "state_change" : {"in_air" : "True"}},
                            {"action" : "fly_to_medkit",
                               "state_change" : {"near_medkit" : "True"}},
                            {"action" : "pickup_medkit",
                               "state_change" : {"has_medkit" : "True", "bay_empty" : "False"}},
                            {"action" : "fly_to_hikers",
                               "state_change" : {"near_hikers" : "True"}},
                            {"action" : "drop_medkit",
                               "state_change" : {"hikers_w_medkit" : "True"}}
                        ]
                }

        }"""

# print(f't2: {t2}')

tp2 = """{
                    "plan_name" : "Rescue",
                    "start" : {"bay_empty" : "True", "in_air" : "False"},
                    "goal" : {"hikers_w_medkit" : "True"},
                    "sequence":
                        [{"action" : "launch", 
                            "precondition" : {"in_air" : "False"}, 
                            "effect" : {"in_air" : "True"}},
                         {"action" : "fly_to_medkit", 
                            "precondition" : {"in_air" : "True"}, 
                            "effect" : {"near_medkit" : "True"}},
                         {"action" : "pickup_medkit",
                            "precondition" :  {"near_medkit" : "True", "bay_empty" : "True"},
                            "effect" :  {"has_medkit" : "True", "bay_empty" : "False"}},
                         {"action" : "fly_to_hikers",
                            "precondition" :  {"in_air" : "True"},
                            "effect" :  {"near_hikers" : "True"}},
                         {"action" : "drop_medkit",
                            "precondition" :  {"has_medkit" : "True", "near_hikers" : "True"},
                            "effect" : {"hikers_w_medkit" : "True"}}
                        ]
        }"""

print(f'tp2: {tp2}')

pp2 = mylib.json2plan(tp2)
print(pp2)
pp2.display()
pp2.display_encoding()
pp2.display_pop()
pp2.display_all()

te2 = """{
                    "scenario_name" : "RescueScenario",
                    "plan_name" : "Rescue",
                    "start" : {"bay_empty" : "True", "in_air" : "False", "has_medkit" : "False"},
                    "sequence":
                        [
                            {"action" : "launch",
                               "state_change" : {"in_air" : "True"}},
                            {"action" : "fly_to_medkit",
                               "state_change" : {"near_medkit" : "True"}},
                            {"action" : "pickup_medkit",
                               "state_change" : {"has_medkit" : "True", "bay_empty" : "False"}},
                            {"action" : "fly_to_hikers",
                               "state_change" : {"near_hikers" : "True"}},
                            {"action" : "drop_medkit",
                               "state_change" : {"hikers_w_medkit" : "True"}}
                        ]
        }"""

pe2 = mylib.json2scenario(te2)
print(pe2)
pe2.display_execution()

# l2 = json.loads(t2)

# print(f'l2: {l2}')

# print(f'l2 plan_name: {l2["plan_name"]}')
# print(f'l2["plan"]: {l2["plan"]}')
# print(f'l2["execution"]:{l2["execution"]}')

# o2 = json.dumps(l2, indent = 4)

# print(f'json.dumps(l2): {o2}')

mylib.dispatch_scenario("RescueScenario")