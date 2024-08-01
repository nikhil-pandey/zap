import os
import colorsys
import random
import networkx as nx
from pathlib import Path
from collections import defaultdict, namedtuple
from diskcache import Cache
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound
from importlib import resources
from tqdm import tqdm

Tag = namedtuple("Tag", "rel_fname fname line name kind".split())


class CacheManager:
    def __init__(self, root, version=3):
        self.cache_dir = f".aider.tags.cache.v{version}"
        self.path = Path(root) / self.cache_dir
        self.cache = Cache(self.path) if self.path.exists() else None

    def load_cache(self):
        if not self.path.exists():
            return None
        return Cache(self.path)

    def save_cache(self):
        pass

    def get_cache(self):
        return self.cache


class FileProcessor:
    @staticmethod
    def find_src_files(directory):
        if not os.path.isdir(directory):
            return [directory]

        src_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                src_files.append(os.path.join(root, file))
        return src_files

    @staticmethod
    def get_mtime(fname):
        try:
            return os.path.getmtime(fname)
        except FileNotFoundError:
            return None

    @staticmethod
    def read_text(fname):
        try:
            with open(fname, 'rb') as f:
                content = f.read()
                if b'\0' in content:
                    return None  # Return None if binary content is detected
                return content.decode('utf-8')
        except FileNotFoundError:
            return None


class TagExtractor:
    def __init__(self, io):
        self.io = io

    def get_tags(self, fname, rel_fname, cache):
        file_mtime = FileProcessor.get_mtime(fname)
        if file_mtime is None:
            return []

        cache_key = fname
        if cache_key in cache and cache[cache_key]["mtime"] == file_mtime:
            return cache[cache_key]["data"]

        data = list(self.get_tags_raw(fname, rel_fname))

        cache[cache_key] = {"mtime": file_mtime, "data": data}
        return data

    def get_tags_raw(self, fname, rel_fname):
        lang = filename_to_lang(fname)
        if not lang:
            return

        language = get_language(lang)
        parser = get_parser(lang)

        query_scm = get_scm_fname(lang)
        if not query_scm.exists():
            return
        query_scm = query_scm.read_text()

        code = self.io.read_text(fname)
        if not code:
            return
        tree = parser.parse(bytes(code, "utf-8"))

        query = language.query(query_scm)
        captures = query.captures(tree.root_node)

        captures = list(captures)

        saw = set()
        for node, tag in captures:
            if tag.startswith("name.definition."):
                kind = "def"
            elif tag.startswith("name.reference."):
                kind = "ref"
            else:
                continue

            saw.add(kind)

            result = Tag(
                rel_fname=rel_fname,
                fname=fname,
                name=node.text.decode("utf-8"),
                kind=kind,
                line=node.start_point[0],
            )

            yield result

        if "ref" in saw:
            return
        if "def" not in saw:
            return

        try:
            lexer = guess_lexer_for_filename(fname, code)
        except ClassNotFound:
            return

        tokens = list(lexer.get_tokens(code))
        tokens = [token[1] for token in tokens if token[0] in Token.Name]

        for token in tokens:
            yield Tag(
                rel_fname=rel_fname,
                fname=fname,
                name=token,
                kind="ref",
                line=-1,
            )


class GraphBuilder:
    def __init__(self, token_count):
        self.token_count = token_count

    def build_graph(self, chat_fnames, other_fnames, mentioned_fnames, mentioned_idents, tag_extractor, cache):
        defines = defaultdict(set)
        references = defaultdict(list)
        definitions = defaultdict(set)
        personalization = dict()

        fnames = set(chat_fnames).union(set(other_fnames))
        chat_rel_fnames = set()
        fnames = sorted(fnames)

        if not fnames:
            return []

        personalize = 100 / len(fnames)

        for fname in tqdm(fnames):
            if not Path(fname).is_file():
                continue

            rel_fname = os.path.relpath(fname)

            if fname in chat_fnames:
                personalization[rel_fname] = personalize
                chat_rel_fnames.add(rel_fname)

            if rel_fname in mentioned_fnames:
                personalization[rel_fname] = personalize

            tags = tag_extractor.get_tags(fname, rel_fname, cache)
            if tags is None:
                continue

            for tag in tags:
                if tag.kind == "def":
                    defines[tag.name].add(rel_fname)
                    key = (rel_fname, tag.name)
                    definitions[key].add(tag)

                if tag.kind == "ref":
                    references[tag.name].append(rel_fname)

        if not references:
            references = dict((k, list(v)) for k, v in defines.items())

        idents = set(defines.keys()).intersection(set(references.keys()))

        G = nx.MultiDiGraph()

        for ident in idents:
            definers = defines[ident]
            if ident in mentioned_idents:
                mul = 10
            elif ident.startswith("_"):
                mul = 0.1
            else:
                mul = 1

            for referencer, num_refs in Counter(references[ident]).items():
                for definer in definers:
                    num_refs = math.sqrt(num_refs)
                    G.add_edge(referencer, definer, weight=mul * num_refs, ident=ident)

        if personalization:
            pers_args = dict(personalization=personalization, dangling=personalization)
        else:
            pers_args = dict()

        ranked = nx.pagerank(G, weight="weight", **pers_args)

        ranked_definitions = defaultdict(float)
        for src in G.nodes:
            src_rank = ranked[src]
            total_weight = sum(data["weight"] for _src, _dst, data in G.out_edges(src, data=True))
            for _src, dst, data in G.out_edges(src, data=True):
                data["rank"] = src_rank * data["weight"] / total_weight
                ident = data["ident"]
                ranked_definitions[(dst, ident)] += data["rank"]

        ranked_tags = []
        ranked_definitions = sorted(ranked_definitions.items(), reverse=True, key=lambda x: x[1])

        for (fname, ident), rank in ranked_definitions:
            if fname in chat_rel_fnames:
                continue
            ranked_tags += list(definitions.get((fname, ident), []))

        rel_other_fnames_without_tags = set(os.path.relpath(fname) for fname in other_fnames)
        fnames_already_included = set(rt[0] for rt in ranked_tags)

        top_rank = sorted([(rank, node) for (node, rank) in ranked.items()], reverse=True)
        for rank, fname in top_rank:
            if fname in rel_other_fnames_without_tags:
                rel_other_fnames_without_tags.remove(fname)
            if fname not in fnames_already_included:
                ranked_tags.append((fname,))

        for fname in rel_other_fnames_without_tags:
            ranked_tags.append((fname,))

        return ranked_tags


class RepoMap:
    def __init__(self, repo_path, io, token_count):
        self.repo_path = repo_path
        self.io = io
        self.cache_manager = CacheManager(repo_path)
        self.tag_extractor = TagExtractor(io)
        self.graph_builder = GraphBuilder(token_count)

    def generate_map(self, chat_fnames, other_fnames, mentioned_fnames=None, mentioned_idents=None,
                     max_map_tokens=None):
        if not chat_fnames and not other_fnames:
            return None

        cache = self.cache_manager.load_cache()
        ranked_tags = self.graph_builder.build_graph(chat_fnames, other_fnames, mentioned_fnames, mentioned_idents,
                                                     self.tag_extractor, cache)
        num_tags = len(ranked_tags)
        lower_bound = 0
        upper_bound = num_tags
        best_tree = None
        best_tree_tokens = 0
        chat_rel_fnames = [os.path.relpath(fname) for fname in chat_fnames]
        middle = min(max_map_tokens // 25, num_tags)
        while lower_bound <= upper_bound:
            tree = self._to_tree(ranked_tags[:middle], chat_rel_fnames)
            num_tokens = self.io.token_count(tree)
            if num_tokens < max_map_tokens and num_tokens > best_tree_tokens:
                best_tree = tree
                best_tree_tokens = num_tokens
            if num_tokens < max_map_tokens:
                lower_bound = middle + 1
            else:
                upper_bound = middle - 1
            middle = (lower_bound + upper_bound) // 2
        return best_tree

    def _to_tree(self, tags, chat_rel_fnames):
        if not tags:
            return ""

        tags = [tag for tag in tags if tag[0] not in chat_rel_fnames]
        tags = sorted(tags)

        cur_fname = None
        cur_abs_fname = None
        lois = None
        output = ""

        dummy_tag = (None,)
        for tag in tags + [dummy_tag]:
            this_rel_fname = tag[0]

            if this_rel_fname != cur_fname:
                if lois is not None:
                    output += "\n"
                    output += cur_fname + ":\n"
                    output += self._render_tree(cur_abs_fname, cur_fname, lois)
                    lois = None
                elif cur_fname:
                    output += "\n" + cur_fname + "\n"
                if isinstance(tag, Tag):
                    lois = []
                    cur_abs_fname = tag.fname
                cur_fname = this_rel_fname

            if lois is not None:
                lois.append(tag.line)

        output = "\n".join([line[:100] for line in output.splitlines()]) + "\n"
        return output

    def _render_tree(self, abs_fname, rel_fname, lois):
        code = self.io.read_text(abs_fname) or ""
        if not code.endswith("\n"):
            code += "\n"

        context = TreeContext(
            rel_fname,
            code,
            color=False,
            line_number=False,
            child_context=False,
            last_line=False,
            margin=0,
            mark_lois=False,
            loi_pad=0,
        )

        context.add_lines_of_interest(lois)
        context.add_context()
        return context.format()


def get_random_color():
    hue = random.random()
    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1, 0.75)]
    return f"#{r:02x}{g:02x}{b:02x}"


def get_scm_fname(lang):
    try:
        return resources.files(__package__).joinpath("queries", f"tree-sitter-{lang}-tags.scm")
    except KeyError:
        return


def filename_to_lang(filename):
    # Dummy implementation, replace with actual logic
    return 'python'


if __name__ == "__main__":
    import sys
    from aider.dump import dump

    fnames = sys.argv[1:]
    io = FileProcessor()

    chat_fnames = []
    other_fnames = []
    for fname in fnames:
        if Path(fname).is_dir():
            chat_fnames += io.find_src_files(fname)
        else:
            chat_fnames.append(fname)

    rm = RepoMap(repo_path=".", io=io, token_count=lambda x: len(x.split()))
    repo_map = rm.generate_map(chat_fnames, other_fnames, max_map_tokens=1024)

    dump(len(repo_map))
    print(repo_map)
