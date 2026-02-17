import utils.directedgraph as dg
import actionmodel.statespace as ss
import plancompilation.partialorderplan as pp

# Identifies a subset of the orderings of a partial order plan that, together with the causal links, imply all other orderings.
# Used to ensure the plan is "least commitment".

def remove_dominated_orderings(graph: dg.DirectedGraph, orderings: list[pp.Ordering]) -> list[pp.Ordering]:
    # Return a minimal subset of orderings that, together with links, imply all removed orderings.

    # Construct a directed graph that represents the causal links and orderings.
    graph = add_orderings_to_graph(graph, orderings)

    # Identify spanning tree of graph, while selecting links over orderings.
    # Spanning tree contains the minimal set of orderings.
    graph.mark_preferred_spanning_tree()

    # extract orderings that are marked in the graph.
    return marked_orderings(orderings,graph)


def graph_for_actions_and_links(start: ss.Action, actions: list[ss.Action], links: list[pp.CausalLink]) -> dg.DirectedGraph:
    # Returns a directed graph that represents connections between actions,
    # that are established by the causal links.
    # Causal links are labeled with priority 1.

    # - Start vertex corresponds to start action.
    graph = dg.DirectedGraph(actions)

    for action in actions:
        graph.add_vertex(action, action == start)

    for link in links:
        graph.add_edge(link, link.producer, link.consumer,1)

    return graph


def add_orderings_to_graph(graph: dg.DirectedGraph, orderings: list[pp.Ordering]) -> dg.DirectedGraph:
    # Takes as input a directed graph that represents all actions and causal links.
    # Adds orderings to graph and returns it.
    # Orderings are labeled with priority 2.

    for ordering in orderings:
        graph.add_edge(ordering, ordering.predecessor, ordering.successor,2)

    return graph

def marked_orderings(orderings: list[pp.Ordering], graph: dg.DirectedGraph)-> list[pp.Ordering]:
    # Returns orderings that are marked in graph.

    morderings = []
    for ordering in orderings:
        edge = graph.edge_named[ordering]
        if edge.mark:
            morderings.append(edge)
    return morderings
