from typing import List, Dict
from models import GraphNode, Tag
import networkx as nx


class RepoMap:
    def __init__(self, graph: Dict[str, GraphNode]):
        self.graph = graph
        self.nx_graph = self._create_nx_graph()

    def _create_nx_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        for file, node in self.graph.items():
            G.add_node(file)
            for ref in node.references:
                for def_file, def_node in self.graph.items():
                    if ref in def_node.definitions:
                        G.add_edge(file, def_file, ident=ref)
        return G

    def get_ranked_tags_map(self, focus_files: List[str], max_files: int) -> List[Tag]:
        personalization = {file: 1 for file in focus_files}
        ranked = nx.pagerank(self.nx_graph, personalization=personalization)

        sorted_files = sorted(ranked.items(), key=lambda x: x[1], reverse=True)[:max_files]

        ranked_tags = []
        for file, _ in sorted_files:
            ranked_tags.extend(self.graph[file].tags)

        return ranked_tags
