A simple plan executive for classic, PDDL-like plans (STRIPS plans).

Takes as input a total order plan and dispatches plan actions to a robot, while monitoring the robot state to confirm correct results.

A classic plan is a sequence of atomic actions that are performed instantaneously,
together with descriptions of the preconditions that each action requires and the intended effects of each action.

preconditions and effects, as well as the state of the robot are represented by a set of propositions 
(e.g., "robot at home") and assignments of true or false to these propositions

The robot is commanded by sending an action name and by acknowledging when the action is completed.
The robot reports any change in its state, in terms of propositions that have changed between true and false.

The plan executive analysis the input plan to confirm correctness, do identify flexibility in the order in 
which actions can be performed, and to identify state conditions that need to hold during plan execution 
to preserve correctness.  The result of this analysis is a least committment plan, which specifies required
orderings between actions and causal links, which specify conditions that must hold from the end of one 
action to the start of another.

Plan execution involves repeatedly identifying a set of actions that can be performed next (enabled actions),
selecting an enabled action and executing it, identifying (active) state conditions that need to hold, 
observing robot state, and comparing this state against the active state conditions.
If a state condition is not met, the robot flags an error and provides an explanation for that failure.
