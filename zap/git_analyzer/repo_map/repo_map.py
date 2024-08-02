from typing import List, Dict
from zap.git_analyzer.repo_map.models import GraphNode, Tag, FileInfo
import networkx as nx


class RepoMap:
    def __init__(self, graph: Dict[str, GraphNode], file_infos: Dict[str, FileInfo]):
        self.graph = graph
        self.file_infos = file_infos
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

    def get_ranked_tags_map(self, focus_files: list[str], max_files: int, max_tags_per_file: int = 50) -> list[Tag]:
        personalization = {file: 1 for file in focus_files}
        ranked = nx.pagerank(self.nx_graph, personalization=personalization)

        sorted_files = sorted(ranked.items(), key=lambda x: x[1], reverse=True)[:max_files]

        ranked_tags = []
        for file, _ in sorted_files:
            if file in self.file_infos:
                ranked_tags.extend(self.file_infos[file].tags[:max_tags_per_file])

        return ranked_tags[:max_files * max_tags_per_file]
