# Project RobustExecution

# Exercising basic routines for extracting the least commitment plan.

# To run this scratch file from any project:
import sys
sys.path.insert(0,'/Users/brian/PycharmProjects/robustExecution/robust-execution')

import utils.utils as ut
import model.states.assignment as asn
import model.actions.action as at
import plancompiler.extractpartialorderplan as ex
import model.plans.totalorderplan as tp

print('This scratch file exercises basic routines for constructing, abstracting and displaying plans.')

# a = ["a", "b"]
# print(a)

a1 = asn.Assignment("P", True)
a1f = asn.Assignment("P", False)
a2 = asn.Assignment("Q", True)
a2f = asn.Assignment("Q", False)

# print(a1)
# print(a2)

pre = [a1, a2]

#print(pre)

#st = ""
#first = True
#for p in pre:
#    if first:
#        st = st + str(p)
#        first = False
#    else:
#        st = st + "," + str(p)
#print(st)

# pres = utils.string_for_list_of_objects(pre)

# print(pres)

eff = [a2f]

pre2 = [a2f]
eff2 = [a1f]
#effs = utils.string_for_list_of_objects(eff)

#print(effs)

print()
print('Planning problem elements:')

plan_name = "P1"

print(f'Plan Name: {plan_name}')

start = pre
print(f'Start: {ut.list2string(start)}')

goal = eff2
print(f'Goal: {ut.list2string(goal)}')

print()
print('Actions:')

act1 = at.Action("A1", pre, eff)
print(act1)

act2 = at.Action("A2", pre2, eff2)
print(act2)

# s1 = ss.State(pre)
# print(s1)

# print(f"{"Q"}:{s1.value("Q")}")

#s1.assign_value("Q",False)

# print(s1)

#b1 = bot.Bot("rob", False, False)
#print(b1)

#ea = [act1,act2]
#sa = b1.select_enabled_action(ea)

#b1.perform_action(sa)
#print("Done")

#ed = {"a1": act1, "a2": act2}

#print(ed)

#edv = ed.values()
#print(type(list(edv)))

plan = [act1, act2]

print()
print('Grounded action sequence:')
print(ut.list2string(plan))

es1 = tp.encode_total_order_plan(plan, start, goal)

print()
print('Encoding of grounded plan:')
print(ut.list2string(es1))

print('Extracting partial order plan elements, one at a time, from the grounded plan:')
cl1 = ex.extract_causal_links(plan_name, es1)
print()
print('  Causal links:')
if cl1 is None:
    print('No causal links.')
else:
    for lnk in cl1:
        print(lnk)

o1, th1 = ex.extract_orderings(es1,cl1)
print()
print('  Orderings:')

if o1 is None:
    print('No orderings.')
else:
    for ord1 in o1:
        print(ord1)

print()
print('  Threats:')

if th1 is None:
    print('No threats.')
else:
    for th in th1:
        print(th)

# pop_plan, threats = ex.extract_partial_order_plan("Test Plan", es1)

# pl1 = tp.TotalOrderPlan("Plan 1", [act1, act2], start, goal)

# For <start, goal, plan>, create total order plan, its encoding and its partial order plan.

print('')
print('Creating the plan as a total order plan object and displaying:')

top1 = tp.TotalOrderPlan(plan_name, plan, start, goal)

print()
top1.display()

print()
print('Displaying total order plan, its encoding and its partial order plan:')

print()
top1.display_all()

# Setup dispatcher for the plan.

# print()
# print('Setting up a dispatcher for this plan.')

# disp1 =  pd.Dispatcher("Pike", top1)

# Dispatch the plan.
# pd.dispatch_plan(disp1)