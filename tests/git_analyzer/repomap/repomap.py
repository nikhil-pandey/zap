import shutil
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock

from zap.git_analyzer.repomap import *


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_initialization(self):
        self.assertEqual(self.cache_manager.cache_dir, f".aider.tags.cache.v3")

    def test_load_cache(self):
        self.assertIsNone(self.cache_manager.load_cache())
        os.makedirs(self.cache_manager.path)
        self.assertIsNotNone(self.cache_manager.load_cache())

    def test_get_cache(self):
        self.assertIsNone(self.cache_manager.get_cache())

    def test_save_cache(self):
        self.cache_manager.save_cache()
        self.assertTrue(True)


class TestFileProcessor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_find_src_files_directory(self):
        os.makedirs(os.path.join(self.tmpdir, "subdir"))
        with open(os.path.join(self.tmpdir, "file1.py"), "w"):
            pass
        with open(os.path.join(self.tmpdir, "subdir", "file2.py"), "w"):
            pass
        result = FileProcessor.find_src_files(self.tmpdir)
        self.assertEqual(len(result), 2)

    def test_find_src_files_single_file(self):
        file_path = os.path.join(self.tmpdir, "file1.py")
        with open(file_path, "w"):
            pass
        result = FileProcessor.find_src_files(file_path)
        self.assertEqual(result, [file_path])

    def test_find_src_files_empty_directory(self):
        result = FileProcessor.find_src_files(self.tmpdir)
        self.assertEqual(result, [])

    def test_get_mtime_existing_file(self):
        file_path = os.path.join(self.tmpdir, "file1.py")
        with open(file_path, "w"):
            pass
        mtime = FileProcessor.get_mtime(file_path)
        self.assertIsNotNone(mtime)

    def test_get_mtime_non_existing_file(self):
        mtime = FileProcessor.get_mtime("non_existing_file.py")
        self.assertIsNone(mtime)

    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_read_text_existing_file(self, mock_file):
        result = FileProcessor.read_text("file1.py")
        self.assertEqual(result, "file content")

    def test_read_text_non_existing_file(self):
        result = FileProcessor.read_text("non_existing_file.py")
        self.assertIsNone(result)

    def test_read_text_binary_file(self):
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        with patch("builtins.open", mock_open(read_data=binary_content), create=True):
            result = FileProcessor.read_text("binary_file.png")
            self.assertIsNone(result)


class TestTagExtractor(unittest.TestCase):
    def setUp(self):
        self.io = MagicMock()
        self.tag_extractor = TagExtractor(self.io)

    @patch.object(FileProcessor, 'get_mtime', return_value=123456789)
    def test_get_tags_from_cache(self, mock_get_mtime):
        cache = {
            "file1.py": {"mtime": 123456789, "data": [Tag("file1.py", "file1.py", 1, "def_name", "def")]}
        }
        result = self.tag_extractor.get_tags("file1.py", "file1.py", cache)
        self.assertEqual(result, [Tag("file1.py", "file1.py", 1, "def_name", "def")])

    @patch.object(FileProcessor, 'get_mtime', return_value=123456789)
    @patch.object(TagExtractor, 'get_tags_raw', return_value=[Tag("file1.py", "file1.py", 1, "def_name", "def")])
    def test_get_tags_no_cache(self, mock_get_tags_raw, mock_get_mtime):
        cache = {}
        result = self.tag_extractor.get_tags("file1.py", "file1.py", cache)
        self.assertEqual(result, [Tag("file1.py", "file1.py", 1, "def_name", "def")])

    @patch("zap.git_analyzer.repomap.filename_to_lang", return_value="python")
    @patch("zap.git_analyzer.repomap.get_language")
    @patch("zap.git_analyzer.repomap.get_parser")
    def test_get_tags_raw(self, mock_get_parser, mock_get_language, mock_filename_to_lang):
        self.io.read_text.return_value = "def my_function():\n    pass"
        mock_get_language.return_value.query.return_value.captures.return_value = []
        result = list(self.tag_extractor.get_tags_raw("file1.py", "file1.py"))
        self.assertTrue(any(tag.kind == "def" for tag in result))

    @patch("zap.git_analyzer.repomap.filename_to_lang", return_value="python")
    @patch("zap.git_analyzer.repomap.get_language")
    @patch("zap.git_analyzer.repomap.get_parser")
    def test_get_tags_raw_complex_code(self, mock_get_parser, mock_get_language, mock_filename_to_lang):
        self.io.read_text.return_value = """
        def outer_function():
            def inner_function():
                pass
        """
        mock_get_language.return_value.query.return_value.captures.return_value = []
        result = list(self.tag_extractor.get_tags_raw("file1.py", "file1.py"))
        self.assertTrue(any(tag.kind == "def" and tag.name == "outer_function" for tag in result))
        self.assertTrue(any(tag.kind == "def" and tag.name == "inner_function" for tag in result))

    @patch("zap.git_analyzer.repomap.filename_to_lang", return_value=None)
    def test_get_tags_raw_no_language(self, mock_filename_to_lang):
        self.io.read_text.return_value = ""
        result = list(self.tag_extractor.get_tags_raw("file1.py", "file1.py"))
        self.assertEqual(result, [])

    def test_get_tags_invalid_cache(self):
        cache = {"file1.py": {"mtime": 123456789, "data": None}}
        result = self.tag_extractor.get_tags("file1.py", "file1.py", cache)
        self.assertEqual(result, [])


class TestGraphBuilder(unittest.TestCase):
    def setUp(self):
        self.token_count = lambda x: len(x.split())
        self.graph_builder = GraphBuilder(self.token_count)
        self.tag_extractor = MagicMock()

    @patch.object(FileProcessor, 'get_mtime', return_value=123456789)
    def test_build_graph_minimal(self, mock_get_mtime):
        cache = {}
        self.tag_extractor.get_tags.return_value = [
            Tag("file1.py", "file1.py", 1, "def_name", "def"),
            Tag("file1.py", "file1.py", 2, "ref_name", "ref")
        ]
        ranked_tags = self.graph_builder.build_graph(["file1.py"], ["file2.py"], set(), set(), self.tag_extractor,
                                                     cache)
        self.assertTrue(ranked_tags)

    @patch.object(FileProcessor, 'get_mtime', return_value=123456789)
    def test_build_graph_complex(self, mock_get_mtime):
        cache = {}
        self.tag_extractor.get_tags.return_value = [
            Tag("file1.py", "file1.py", 1, "def_name", "def"),
            Tag("file1.py", "file1.py", 2, "ref_name", "ref"),
            Tag("file2.py", "file2.py", 1, "def_name", "def")
        ]
        ranked_tags = self.graph_builder.build_graph(["file1.py"], ["file2.py"], set(), set(), self.tag_extractor,
                                                     cache)
        self.assertTrue(ranked_tags)

    @patch.object(FileProcessor, 'get_mtime', return_value=123456789)
    def test_build_graph_cyclic_dependencies(self, mock_get_mtime):
        cache = {}
        self.tag_extractor.get_tags.return_value = [
            Tag("file1.py", "file1.py", 1, "def_a", "def"),
            Tag("file1.py", "file1.py", 2, "ref_b", "ref"),
            Tag("file2.py", "file2.py", 1, "def_b", "def"),
            Tag("file2.py", "file2.py", 2, "ref_a", "ref")
        ]
        ranked_tags = self.graph_builder.build_graph(["file1.py"], ["file2.py"], set(), set(), self.tag_extractor,
                                                     cache)
        self.assertTrue(ranked_tags)

    @patch.object(FileProcessor, 'get_mtime', return_value=123456789)
    def test_build_graph_no_definitions(self, mock_get_mtime):
        cache = {}
        self.tag_extractor.get_tags.return_value = [Tag("file1.py", "file1.py", 2, "ref_name", "ref")]
        ranked_tags = self.graph_builder.build_graph(["file1.py"], ["file2.py"], set(), set(), self.tag_extractor,
                                                     cache)
        self.assertFalse(any(isinstance(tag, Tag) for tag in ranked_tags))


class TestRepoMap(unittest.TestCase):
    def setUp(self):
        self.repo_path = "."
        self.io = MagicMock()
        self.io.token_count = lambda x: int(len(x.split()))
        self.repo_map = RepoMap(self.repo_path, self.io, self.io.token_count)

    @patch.object(RepoMap, '_to_tree', return_value="tree_representation")
    @patch.object(GraphBuilder, 'build_graph', return_value=[Tag("file1.py", "file1.py", 1, "def_name", "def")])
    def test_generate_map(self, mock_build_graph, mock_to_tree):
        result = self.repo_map.generate_map(["file1.py"], ["file2.py"], max_map_tokens=1024)
        self.assertEqual(result, "tree_representation")

    @patch.object(RepoMap, '_to_tree', return_value="tree_representation")
    @patch.object(GraphBuilder, 'build_graph', return_value=[
        Tag("file1.py", "file1.py", 1, "def_name", "def"),
        Tag("file2.py", "file2.py", 2, "ref_name", "ref")
    ])
    def test_generate_map_large(self, mock_build_graph, mock_to_tree):
        result = self.repo_map.generate_map(["file1.py"], ["file2.py"], max_map_tokens=2048)
        self.assertEqual(result, "tree_representation")

    @patch.object(RepoMap, '_to_tree', return_value="tree_representation")
    @patch.object(GraphBuilder, 'build_graph', return_value=[Tag("file1.py", "file1.py", 1, "def_name", "def")])
    def test_generate_map_with_mentions(self, mock_build_graph, mock_to_tree):
        result = self.repo_map.generate_map(["file1.py"], ["file2.py"], mentioned_fnames={"file1.py"},
                                            mentioned_idents={"def_name"}, max_map_tokens=1024)
        self.assertEqual(result, "tree_representation")

    def test_generate_map_empty(self):
        result = self.repo_map.generate_map([], [], max_map_tokens=1024)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
