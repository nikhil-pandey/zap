import unittest
import tempfile
import os
from zap.git_analyzer.repo_map.repo_analyzer import RepoAnalyzer
from zap.git_analyzer.repo_map.repo_map import RepoMap
from zap.git_analyzer.repo_map.config import Config
import networkx as nx

class TestRepoMap(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.test_dir.name
        self.config = Config()
        self.repo_analyzer = RepoAnalyzer(self.repo_path, self.config)

        self.python_file_content = """
        class SampleClass:
            def method_one(self):
                pass

        def sample_function():
            pass
        """
        self.python_file_path = os.path.join(self.repo_path, 'sample.py')
        with open(self.python_file_path, 'w') as f:
            f.write(self.python_file_content)

        self.csharp_file_content = """
        using System;

        namespace SampleNamespace
        {
            class SampleClass
            {
                void MethodOne() {}
            }

            class AnotherClass
            {
                void AnotherMethod() {}
            }
        }
        """
        self.csharp_file_path = os.path.join(self.repo_path, 'sample.cs')
        with open(self.csharp_file_path, 'w') as f:
            f.write(self.csharp_file_content)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_pagerank_calculation(self):
        file_infos = self.repo_analyzer.analyze_files(['sample.py', 'sample.cs'])
        graph = self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        repo_map.calculate_pagerank(['sample.py'], set())

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')
        self.assertGreater(ranks['sample.py'], 0)
        self.assertGreater(ranks['sample.cs'], 0)

    def test_get_ranked_tags_map(self):
        file_infos = self.repo_analyzer.analyze_files(['sample.py', 'sample.cs'])
        graph = self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        ranked_tags = repo_map.get_ranked_tags_map(['sample.py'], set(), max_files=2, max_tags_per_file=2)
        self.assertGreater(len(ranked_tags), 0)

if __name__ == '__main__':
    unittest.main()
