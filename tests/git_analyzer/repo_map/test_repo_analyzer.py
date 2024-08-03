import unittest
import tempfile
import os
from zap.git_analyzer.repo_map.code_analyzer import CodeAnalyzer
from zap.git_analyzer.repo_map.codeanalyzerconfig import CodeAnalyzerConfig


class TestRepoAnalyzer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.test_dir.name
        self.config = CodeAnalyzerConfig()
        self.repo_analyzer = CodeAnalyzer(self.repo_path, self.config)

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

    def test_analyze_files(self):
        file_infos = self.repo_analyzer.analyze_files(['sample.py', 'sample.cs'])
        self.assertIn('sample.py', file_infos)
        self.assertIn('sample.cs', file_infos)
        self.assertEqual(len(file_infos['sample.py'].tags), 3)
        self.assertEqual(len(file_infos['sample.cs'].tags), 5)

    def test_build_graph(self):
        file_infos = self.repo_analyzer.analyze_files(['sample.py', 'sample.cs'])
        graph = self.repo_analyzer.build_graph(file_infos)
        self.assertIn('sample.py', graph)
        self.assertIn('sample.cs', graph)
        self.assertEqual(len(graph['sample.py'].definitions), 3)
        self.assertEqual(len(graph['sample.cs'].definitions), 5)


if __name__ == '__main__':
    unittest.main()
