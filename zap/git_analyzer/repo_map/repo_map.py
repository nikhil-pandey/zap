from typing import List, Dict, Set
from zap.git_analyzer.repo_map.models import GraphNode, Tag, FileInfo
import networkx as nx
import logging

LOGGER = logging.getLogger("git_analyzer")


class RepoMap:
    def __init__(self, graph: Dict[str, GraphNode], file_infos: Dict[str, FileInfo]):
        self.graph = graph
        self.file_infos = file_infos
        self.nx_graph = self._create_nx_graph()
        LOGGER.info("RepoMap initialized")

    def _create_nx_graph(self) -> nx.MultiDiGraph:
        G = nx.MultiDiGraph()
        for file, node in self.graph.items():
            G.add_node(file)
            for ref in node.references:
                for def_file, def_node in self.graph.items():
                    if ref in def_node.definitions:
                        G.add_edge(file, def_file, ident=ref)
        LOGGER.info(f"NetworkX graph created with {len(G.nodes)} nodes and {len(G.edges)} edges")
        return G

    def calculate_pagerank(self, focus_files: List[str], mentioned_idents: Set[str]) -> None:
        if not focus_files:
            LOGGER.error("Focus files list is empty")
            raise ValueError("Focus files list is empty.")

        personalization = {file: 1.0 / len(focus_files) for file in focus_files}

        idents = set(ref for node in self.graph.values() for ref in node.references).intersection(
            set(d for node in self.graph.values() for d in node.definitions)
        )

        G = nx.MultiDiGraph()
        for ident in idents:
            definers = {file for file, node in self.graph.items() if ident in node.definitions}
            referencers = {file for file, node in self.graph.items() if ident in node.references}
            for definer in definers:
                for referencer in referencers:
                    if definer != referencer:
                        weight = 1.0
                        if ident in mentioned_idents:
                            weight *= 10
                        elif ident.startswith("_"):
                            weight *= 0.1

                        G.add_edge(referencer, definer, weight=weight, ident=ident)

        for file in self.graph:
            if file not in G.nodes:
                G.add_node(file)

        delta = 1 / len(G.nodes)
        for node in G.nodes:
            for other_node in G.nodes:
                if node != other_node:
                    G.add_edge(node, other_node, weight=delta)

        try:
            ranked = nx.pagerank(G, personalization=personalization, alpha=0.85, max_iter=1000)
        except ZeroDivisionError as e:
            LOGGER.error(f"Error in PageRank calculation: {str(e)}")
            raise RuntimeError("Error in PageRank calculation: likely due to insufficient data.") from e

        for node in self.nx_graph.nodes:
            self.nx_graph.nodes[node]['pagerank'] = ranked.get(node, 0)
        LOGGER.info("PageRank calculation completed")

    def get_ranked_tags_map(self, focus_files: List[str], mentioned_idents: Set[str], max_files: int,
                            max_tags_per_file: int = 50) -> List[Tag]:
        self.calculate_pagerank(focus_files, mentioned_idents)

        ranked = nx.get_node_attributes(self.nx_graph, 'pagerank')
        sorted_files = sorted(ranked.items(), key=lambda x: x[1], reverse=True)[:max_files]

        ranked_tags = []
        for file, _ in sorted_files:
            if file in self.file_infos:
                ranked_tags.extend(self.file_infos[file].tags[:max_tags_per_file])

        LOGGER.info(f"Ranked tags map generated with {len(ranked_tags)} tags")
        return ranked_tags[:max_files * max_tags_per_file]
