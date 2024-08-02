import unittest
import tempfile
import os
from zap.git_analyzer.repo_map.tag_extractor import TagExtractor


class TestTagExtractor(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.test_dir.name

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

        self.tag_extractor = TagExtractor(self.repo_path)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_python_tag_extraction(self):
        tags = self.tag_extractor.extract_tags(self.python_file_path, self.python_file_content)
        self.assertEqual(len(tags), 3)
        self.assertTrue(any(tag.name == 'SampleClass' for tag in tags))
        self.assertTrue(any(tag.name == 'method_one' for tag in tags))
        self.assertTrue(any(tag.name == 'sample_function' for tag in tags))

    def test_csharp_tag_extraction(self):
        tags = self.tag_extractor.extract_tags(self.csharp_file_path, self.csharp_file_content)
        self.assertEqual(len(tags), 9)
        self.assertTrue(any(tag.name == 'SampleClass' for tag in tags))
        self.assertTrue(any(tag.name == 'AnotherClass' for tag in tags))
        self.assertTrue(any(tag.name == 'AnotherMethod' for tag in tags))
        self.assertTrue(any(tag.name == 'CompositeClass' for tag in tags))
        self.assertTrue(any(tag.name == 'CompositeMethod' for tag in tags))

    def test_empty_file(self):
        empty_file_path = os.path.join(self.repo_path, 'empty.py')
        with open(empty_file_path, 'w'):
            pass
        tags = self.tag_extractor.extract_tags(empty_file_path, "")
        self.assertEqual(len(tags), 0)

    def test_invalid_syntax_file_does_not_return(self):
        invalid_syntax_content = """
        def invalid_function(
        """
        invalid_file_path = os.path.join(self.repo_path, 'invalid.py')
        with open(invalid_file_path, 'w') as f:
            f.write(invalid_syntax_content)
        tags = self.tag_extractor.extract_tags(invalid_file_path, invalid_syntax_content)
        self.assertEqual(len(tags), 0)


if __name__ == '__main__':
    unittest.main()
