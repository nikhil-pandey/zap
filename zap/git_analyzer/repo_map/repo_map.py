from typing import List, Dict, Set
from zap.git_analyzer.repo_map.models import GraphNode, Tag, FileInfo
import networkx as nx
import math
from collections import defaultdict, Counter


class RepoMap:
    def __init__(self, graph: Dict[str, GraphNode], file_infos: Dict[str, FileInfo]):
        self.graph = graph
        self.file_infos = file_infos
        self.nx_graph = self._create_nx_graph()

    def _create_nx_graph(self) -> nx.MultiDiGraph:
        G = nx.MultiDiGraph()
        for file, node in self.graph.items():
            G.add_node(file)
            for ref in node.references:
                for def_file, def_node in self.graph.items():
                    if ref in def_node.definitions:
                        G.add_edge(file, def_file, ident=ref)
        return G

    def calculate_pagerank(self, focus_files: List[str], mentioned_idents: Set[str]) -> None:
        if not focus_files:
            raise ValueError("Focus files list is empty.")

        personalization = {file: 1.0 / len(focus_files) for file in focus_files}
        print(f"Personalization vector: {personalization}")

        idents = set(ref for node in self.graph.values() for ref in node.references).intersection(
            set(d for node in self.graph.values() for d in node.definitions)
        )

        G = nx.MultiDiGraph()
        for ident in idents:
            definers = {file for file, node in self.graph.items() if ident in node.definitions}
            referencers = {file for file, node in self.graph.items() if ident in node.references}

            for definer in definers:
                for referencer in referencers:
                    if definer != referencer:  # Avoid self-loops
                        weight = math.sqrt(1)  # Assuming 1 reference for simplicity
                        if ident in mentioned_idents:
                            weight *= 10
                        elif ident.startswith("_"):
                            weight *= 0.1

                        # Debug statement to log the weight adjustment
                        print(f"Creating edge {referencer} -> {definer} with weight {weight} for ident {ident}")

                        G.add_edge(referencer, definer, weight=weight, ident=ident)

        # Debug: Print the nodes and edges of the graph
        print("Graph Nodes:")
        for node in G.nodes:
            print(node)

        print("Graph Edges:")
        for edge in G.edges(data=True):
            print(edge)

        try:
            ranked = nx.pagerank(G, personalization=personalization)
        except ZeroDivisionError as e:
            raise RuntimeError("Error in PageRank calculation: likely due to insufficient data.") from e

        for node in self.nx_graph.nodes:
            self.nx_graph.nodes[node]['pagerank'] = ranked.get(node, 0)

        # Debug: Print out the PageRank values
        print("PageRank values:")
        for node, rank in ranked.items():
            print(f"{node}: {rank}")

    def get_ranked_tags_map(self, focus_files: List[str], mentioned_idents: Set[str], max_files: int,
                            max_tags_per_file: int = 50) -> List[Tag]:
        self.calculate_pagerank(focus_files, mentioned_idents)

        ranked = nx.get_node_attributes(self.nx_graph, 'pagerank')
        sorted_files = sorted(ranked.items(), key=lambda x: x[1], reverse=True)[:max_files]

        ranked_tags = []
        for file, _ in sorted_files:
            if file in self.file_infos:
                ranked_tags.extend(self.file_infos[file].tags[:max_tags_per_file])

        return ranked_tags[:max_files * max_tags_per_file]
