from typing import Any

# Basic operations on a directed graph.

class DGVertex:
    def __init__(self, name: Any, startp: bool) -> None:
        self.name = name
        self.startp = startp
        self.out_edges = []
        self.in_edges = []
        self.mark = False


    def __str__(self):
        if self.startp:
            return f"{self.name}(S)"
        else:
            return f"{self.name}"


class DGEdge:
    def __init__(self, name: Any, source: DGVertex, target: DGVertex, priority: int) -> None:
        self.name = name
        self.source = source
        self.target = target
        self.priority = priority
        source.out_edges.append(self)
        target.in_edges.append(self)
        self.mark = False


    def __str__(self):
        if self.name:
            return f"[{self.name}, {self.source}, {self.target}]"
        else:
            return f"[{self.source}, {self.target}]"


def edge_priority(edge: DGEdge) -> int:
    return edge.priority


class DirectedGraph:
    def __init__(self, name):
        self.name = name
        self.start = None
        self.vertices = []
        self.edges = []
        self.vertex_named = dict()
        self.edge_named = dict()


    def __str__(self):
        return f"{self.name}"


    def describe_graph(self, markedp: bool = False):
        # Print a description of Graph vertices and edges.
        # If markedp is True, then only print marked vertices and edges,
        # else print all edges and vertices.
        if markedp:
            sv = [str(v) for v in self.vertices if v.mark]
            se = [str(e) for e in self.edges if e.mark]
            print(f"Graph {self.name}, marked vertices {sv}, marked edges: {se}.")
        else:
            sv = [str(v) for v in self.vertices]
            se = [str(e) for e in self.edges]
            print(f"Graph {self.name}, vertices {sv}, edges: {se}.")


    def add_vertex(self, name: Any, startp: bool = False) -> DGVertex:
        # Creates a vertex with name and adds to the vertex dictionary.
        # startp is true if vertex is the start vertex.
        vertex = DGVertex(name, startp)
        self.vertex_named[name] = vertex
        self.vertices.append(vertex)
        if startp:
            self.start = vertex
        return vertex


    def check_has_vertex(self, vertex_name: Any):
        if not vertex_name in self.vertex_named:
            print(f"{vertex_name} is not a vertex of {self}.")


    def get_vertex(self, name: Any, startp: bool = False) -> DGVertex:
        # Retrieves a vertex with name, else creates.
        # startp is true if vertex is the start vertex.
        if  name in self.vertex_named:
            vertex = self.vertex_named[name]
            if startp:
                self.start = vertex
            return vertex
        else:
            return self.add_vertex(name, startp)


    def add_edge(self, edge_name: Any, source_name: Any, target_name: Any, priority: int) -> DGEdge:
        # Creates an edge with edge_name and priority, from the vertex of source_name to the vertex of target_name.
        # Adds to the edge dictionary.  Creates vertices if they don't exist.
        source = self.get_vertex(source_name)
        target = self.get_vertex(target_name)
        edge = DGEdge(edge_name, source, target, priority)
        self.edge_named[edge_name] = edge
        self.edges.append(edge)
        return edge


    def path_exists(self, source_name: Any, target_name: Any) -> bool:
        # Returns True if there exists a path in graph from source to target.
        # Creates vertices if they don't exist.

        source = self.get_vertex(source_name)
        target = self.get_vertex(target_name)
        if target == source:
            return True

        # Search depth-first through graph from source to target.
        queue = source.out_edges.copy()
        self.remove_marks()
        source.mark = True

        while queue:
            edge = queue.pop()
            vert = edge.target
            # - Visit a vertex at most once.
            if not vert.mark:

                # - Mark vertex as reached.
                vert.mark = True

                # If target reached, return success.
                if vert == target:
                    return True

                # - Traverse outgoing edges.
                queue.extend(vert.out_edges)

        return False


    def mark_preferred_spanning_tree(self) -> None:
        # Mark edges of graph to form a spanning tree
        # by performing a depth-first-traversal.

        # - Start from the start vertex.
        start = self.start
        if not start:
            print("Missing start for graph {graph}. Can't construct spanning tree.")
        else:
            self.remove_marks()
            queue = start.out_edges.copy()
            start.mark = True

            while queue:
                # Elements are taken off the end of the queue.
                edge = queue.pop()
                vert = edge.target
                # - Visit a vertex at most once.
                if not vert.mark:
                    # - Mark edges that newly visit a vertex as in the spanning tree.
                    edge.mark = True
                    vert.mark = True
                    # - Traverse edges by increasing priority.
                    next_edges = vert.out_edges.copy()
                    # print(f"Next: {next_edges}")
                    # Elements are added to the end of the queue, in decreasing priority.
                    next_edges.sort(key = edge_priority, reverse = True)
                    # print(f"Sorted: {next_edges}")
                    queue.extend(next_edges)


    def remove_marks(self) -> None:
        # Remove marks on vertices and edges of graph

        for vertex in self.vertices:
            vertex.mark = False

        for edge in self.edges:
            edge.mark = False
