# Project RobustExecution

# Tests of directed graph routines

# To run this scratch file from any project:
import sys
sys.path.insert(0,'/Users/brian/PycharmProjects/robustExecution/robust-execution')

print('This scratch file exercises basic routines for constructing and operating on directed graphs.')

import utils.directedgraph as dg

g = dg.DirectedGraph("G1")
g.add_vertex("s",True)
g.add_vertex("b")
g.add_vertex("c")
g.add_vertex("d")
g.add_edge("e1", "s", "b", 1)
g.add_edge("e2", "b", "c", 1)
g.add_edge("e3", "c", "d", 1)
g.add_edge("e4", "b", "d", 2)
g.describe_graph()

haspath = g.path_exists("s","d")
print(f"Has path from s to d? {haspath}")

g.mark_preferred_spanning_tree()
g.describe_graph(True)