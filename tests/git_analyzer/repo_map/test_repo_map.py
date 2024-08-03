import unittest
import tempfile
import os

import pytest

from zap.git_analyzer.repo_map.code_analyzer import CodeAnalyzer
from zap.git_analyzer.repo_map.repo_map import RepoMap
from zap.git_analyzer.repo_map.codeanalyzerconfig import CodeAnalyzerConfig
import networkx as nx


class TestRepoMap(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.test_dir.name
        self.config = CodeAnalyzerConfig(self.repo_path)
        self.repo_analyzer = CodeAnalyzer(self.config)

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

            class CompositeClass {
                void CompositeMethod() {
                    var x = new SampleClass();
                    x.MethodOne();
                }
            }
        }
        """
        self.csharp_file_path = os.path.join(self.repo_path, 'sample.cs')
        with open(self.csharp_file_path, 'w') as f:
            f.write(self.csharp_file_content)

        self.another_python_file_content = """
        from sample import SampleClass

        class AnotherSampleClass:
            def another_method(self):
                instance = SampleClass()
                instance.method_one()
        """
        self.another_python_file_path = os.path.join(self.repo_path, 'another_sample.py')
        with open(self.another_python_file_path, 'w') as f:
            f.write(self.another_python_file_content)

    def tearDown(self):
        self.test_dir.cleanup()

    @pytest.mark.asyncio
    async def test_pagerank_calculation(self):
        file_infos = await self.repo_analyzer.analyze_files(['sample.py', 'sample.cs', 'another_sample.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        repo_map.calculate_pagerank(['sample.py', 'sample.cs', 'another_sample.py'], set())

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')

        # Debug: Print the PageRank values
        print("PageRank values:")
        for node, rank in ranks.items():
            print(f"{node}: {rank}")

        # Assert PageRank values are greater than zero
        self.assertGreater(ranks['sample.py'], 0)
        self.assertGreater(ranks['sample.cs'], 0)
        self.assertGreater(ranks['another_sample.py'], 0)

    @pytest.mark.asyncio
    async def test_get_ranked_tags_map(self):
        file_infos = await self.repo_analyzer.analyze_files(['sample.py', 'sample.cs', 'another_sample.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        ranked_tags = repo_map.get_ranked_tags_map(['sample.py'], set(), max_files=2, max_tags_per_file=2)
        self.assertGreater(len(ranked_tags), 0)

    @pytest.mark.asyncio
    async def test_isolated_file(self):
        isolated_file_content = """
        class IsolatedClass:
            def isolated_method(self):
                pass
        """
        isolated_file_path = os.path.join(self.repo_path, 'isolated.py')
        with open(isolated_file_path, 'w') as f:
            f.write(isolated_file_content)

        file_infos = await self.repo_analyzer.analyze_files(
            ['sample.py', 'sample.cs', 'another_sample.py', 'isolated.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        repo_map.calculate_pagerank(['sample.py', 'sample.cs', 'another_sample.py', 'isolated.py'], set())

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')

        # Debug: Print the PageRank values
        print("PageRank values with isolated file:")
        for node, rank in ranks.items():
            print(f"{node}: {rank}")

        self.assertGreater(ranks['isolated.py'], 0)
        self.assertLess(ranks['isolated.py'], 0.2)

    @pytest.mark.asyncio
    async def test_circular_references(self):
        circular_file_content_1 = """
        from circular2 import CircularClass2

        class CircularClass1:
            def method1(self):
                instance = CircularClass2()
                instance.method2()
        """
        circular_file_content_2 = """
        from circular1 import CircularClass1

        class CircularClass2:
            def method2(self):
                instance = CircularClass1()
                instance.method1()
        """
        circular_file_path_1 = os.path.join(self.repo_path, 'circular1.py')
        with open(circular_file_path_1, 'w') as f:
            f.write(circular_file_content_1)

        circular_file_path_2 = os.path.join(self.repo_path, 'circular2.py')
        with open(circular_file_path_2, 'w') as f:
            f.write(circular_file_content_2)

        file_infos = await self.repo_analyzer.analyze_files(['circular1.py', 'circular2.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        repo_map.calculate_pagerank(['circular1.py', 'circular2.py'], set())

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')

        # Debug: Print the PageRank values
        print("PageRank values with circular references:")
        for node, rank in ranks.items():
            print(f"{node}: {rank}")

        # Assert PageRank values are greater than zero
        self.assertGreater(ranks['circular1.py'], 0)
        self.assertGreater(ranks['circular2.py'], 0)

    @pytest.mark.asyncio
    async def test_pagerank_with_different_weights(self):
        file_infos = await self.repo_analyzer.analyze_files(['sample.py', 'sample.cs', 'another_sample.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)

        # Debug: Print initial file_infos and graph
        print("File Infos:")
        for file, info in file_infos.items():
            print(file, info)

        print("Graph:")
        for node, data in graph.items():
            print(node, data)

        repo_map.calculate_pagerank(['sample.py', 'sample.cs'], {'method_one', 'SampleClass'})

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')

        # Debug: Print the PageRank values
        print("PageRank values with different weights:")
        for node, rank in ranks.items():
            print(f"{node}: {rank}")

        # Assert PageRank values reflect the mentioned identifiers influence
        self.assertGreater(ranks['sample.py'], 0)
        self.assertGreater(ranks['sample.cs'], 0)
        self.assertGreater(ranks['another_sample.py'], 0)

    @pytest.mark.asyncio
    async def test_pagerank_with_no_focus_files(self):
        file_infos = await self.repo_analyzer.analyze_files(['sample.py', 'sample.cs', 'another_sample.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        with self.assertRaises(ValueError):
            repo_map.calculate_pagerank([], set())

    @pytest.mark.asyncio
    async def test_frequently_mentioned_identifiers(self):
        file_infos = await self.repo_analyzer.analyze_files(['sample.py', 'sample.cs', 'another_sample.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        repo_map.calculate_pagerank(['sample.py', 'sample.cs'], {'SampleClass', 'method_one'})

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')

        # Debug: Print the PageRank values
        print("PageRank values with frequently mentioned identifiers:")
        for node, rank in ranks.items():
            print(f"{node}: {rank}")

        # Assert PageRank values reflect the influence of frequently mentioned identifiers
        self.assertGreater(ranks['sample.py'], 0)
        self.assertGreater(ranks['sample.cs'], 0)
        self.assertGreater(ranks['another_sample.py'], 0)

    @pytest.mark.asyncio
    async def test_sparsely_mentioned_identifiers(self):
        file_infos = await self.repo_analyzer.analyze_files(['sample.py', 'sample.cs', 'another_sample.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        repo_map.calculate_pagerank(['sample.py', 'sample.cs'], {'sample_function'})

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')

        # Debug: Print the PageRank values
        print("PageRank values with sparsely mentioned identifiers:")
        for node, rank in ranks.items():
            print(f"{node}: {rank}")

        # Assert PageRank values reflect the influence of sparsely mentioned identifiers
        self.assertGreater(ranks['sample.py'], 0)
        self.assertGreater(ranks['sample.cs'], 0)

    @pytest.mark.asyncio
    async def test_identifiers_mentioned_across_multiple_files(self):
        file_infos = await self.repo_analyzer.analyze_files(['sample.py', 'sample.cs', 'another_sample.py'])
        graph = await self.repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)
        repo_map.calculate_pagerank(['sample.py', 'sample.cs'], {'SampleClass', 'CompositeClass'})

        ranks = nx.get_node_attributes(repo_map.nx_graph, 'pagerank')

        # Debug: Print the PageRank values
        print("PageRank values with identifiers mentioned across multiple files:")
        for node, rank in ranks.items():
            print(f"{node}: {rank}")

        # Assert PageRank values reflect the influence of identifiers mentioned across multiple files
        self.assertGreater(ranks['sample.py'], 0)
        self.assertGreater(ranks['sample.cs'], 0)
        self.assertGreater(ranks['another_sample.py'], 0)


if __name__ == '__main__':
    unittest.main()
