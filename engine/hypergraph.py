# engine/hypergraph.py
import random
import itertools
from collections import defaultdict


class Vertex:
    """
    Fundamental event.
    """
    _id_counter = itertools.count()

    def __init__(self):
        self.id = next(Vertex._id_counter)
        self.depth = 1  # Worldline (causal) depth

    def __repr__(self):
        return f"V{self.id}"


class Hyperedge:
    """
    k-ary relation between vertices.
    """
    _id_counter = itertools.count()

    def __init__(self, vertices):
        self.id = next(Hyperedge._id_counter)
        self.vertices = tuple(vertices)

    def __repr__(self):
        ids = ",".join(str(v.id) for v in self.vertices)
        return f"E{self.id}({ids})"


class Hypergraph:
    """
    Core data structure for HCSN.
    Represents a causal quantum hypergraph.
    """

    def __init__(self):
        self.vertices = {}
        self.hyperedges = {}
        self.causal_order = defaultdict(set)  # u.id -> set of v.id

    # ---------- Vertex operations ----------

    def add_vertex(self):
        v = Vertex()
        
        #NEW: topological/charge-like label
        v.label = random.choice([-1, +1])
        self.vertices[v.id] = v
        self.causal_order[v.id].add(v.id)  # reflexivity
        return v

    # ---------- Hyperedge operations ----------

    def add_hyperedge(self, vertices):
        for v in vertices:
            assert hasattr(v, "id"), f"Non-Vertex in hyperedge: {v}"
        edge = Hyperedge(vertices)
        self.hyperedges[edge.id] = edge
        return edge

    # ---------- Causal structure ----------

    def add_causal_relation(self, u, v):
        """
        Add causal relation u → v and update worldline depth.
        """
        if v.id not in self.causal_order[u.id]:
            self.causal_order[u.id].add(v.id)

            # Worldline inertia: propagate depth
            v.depth = max(v.depth, u.depth + 1)

    def is_causally_related(self, u, v):
        return v.id in self.causal_order[u.id]

    def causal_future(self, v):
        return {self.vertices[i] for i in self.causal_order[v.id]}

    def causal_past(self, v):
        return {
            self.vertices[u_id]
            for u_id in self.vertices
            if v.id in self.causal_order[u_id]
        }

    # ---------- Observables ----------

    def coordination_number(self, v):
        """
        Degree: number of hyperedges containing v.
        """
        return sum(1 for e in self.hyperedges.values() if v in e.vertices)

    def average_coordination(self):
        if not self.vertices:
            return 0.0
        return sum(
            self.coordination_number(v)
            for v in self.vertices.values()
        ) / len(self.vertices)

    # ---------- Worldline inertia ----------

    def max_chain_length(self):
        """
        Maximum causal chain length in the hypergraph.
        """
        if not self.vertices:
            return 0
        return max(v.depth for v in self.vertices.values())

    # ---------- Debug ----------

    def summary(self):
        return {
            "num_vertices": len(self.vertices),
            "num_hyperedges": len(self.hyperedges),
            "avg_coordination": self.average_coordination(),
            "max_chain_length": self.max_chain_length()
        }
