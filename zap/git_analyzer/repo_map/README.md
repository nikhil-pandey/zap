# Repo Map

## Features

1. **PageRank Calculation**: Calculate PageRank values for files in a repository based on their references and
   definitions.
2. **Tag Extraction**: Extract tags for classes, methods, functions, and other identifiers.
3. **Symbol Querying**: Query the repository for specific symbols and retrieve their definitions and references.
4. **Cache Versioning**: Efficiently cache analyzed file data with versioning support to ensure up-to-date results.
5. **Visualization**: Visualize the repository structure using D3.js.

## Usage

### Analyzing a Repository

Use the `main.py` script to analyze a repository:

```bash
python zap/git_analyzer/repo_map/main.py <repo_path> <focus_files> <other_files>
```

### Querying Symbols

You can query the repository for specific symbols using the `query_symbol` method in the `RepoAnalyzer` class.

### Running the Flask Visualization

Run the Flask app to visualize the repository:

```bash
python zap/git_analyzer/repo_map/d3js_visualizer/app.py
```

Then, open your browser and navigate to `http://localhost:5001` to see the visualization.

## Tests

Run the tests using `unittest`:

```bash
python -m unittest discover tests/git_analyzer/repo_map
```

## Credits

ZAP uses tree-sitter repo map from [Aider](https://github.com/paul-gauthier/aider/tree/main/aider/queries) which also
uses the following most tree-sitter queries:

- [https://github.com/tree-sitter/tree-sitter-c](https://github.com/tree-sitter/tree-sitter-c) — licensed under the MIT
  License.
- [https://github.com/tree-sitter/tree-sitter-c-sharp](https://github.com/tree-sitter/tree-sitter-c-sharp) — licensed
  under the MIT License.
- [https://github.com/tree-sitter/tree-sitter-cpp](https://github.com/tree-sitter/tree-sitter-cpp) — licensed under the
  MIT License.
- [https://github.com/Wilfred/tree-sitter-elisp](https://github.com/Wilfred/tree-sitter-elisp) — licensed under the MIT
  License.
- [https://github.com/elixir-lang/tree-sitter-elixir](https://github.com/elixir-lang/tree-sitter-elixir) — licensed
  under the Apache License, Version 2.0.
- [https://github.com/elm-tooling/tree-sitter-elm](https://github.com/elm-tooling/tree-sitter-elm) — licensed under the
  MIT License.
- [https://github.com/tree-sitter/tree-sitter-go](https://github.com/tree-sitter/tree-sitter-go) — licensed under the
  MIT License.
- [https://github.com/tree-sitter/tree-sitter-java](https://github.com/tree-sitter/tree-sitter-java) — licensed under
  the MIT License.
- [https://github.com/tree-sitter/tree-sitter-javascript](https://github.com/tree-sitter/tree-sitter-javascript) —
  licensed under the MIT License.
- [https://github.com/tree-sitter/tree-sitter-ocaml](https://github.com/tree-sitter/tree-sitter-ocaml) — licensed under
  the MIT License.
- [https://github.com/tree-sitter/tree-sitter-php](https://github.com/tree-sitter/tree-sitter-php) — licensed under the
  MIT License.
- [https://github.com/tree-sitter/tree-sitter-python](https://github.com/tree-sitter/tree-sitter-python) — licensed
  under the MIT License.
- [https://github.com/tree-sitter/tree-sitter-ql](https://github.com/tree-sitter/tree-sitter-ql) — licensed under the
  MIT License.
- [https://github.com/r-lib/tree-sitter-r](https://github.com/r-lib/tree-sitter-r) — licensed under the MIT License.
- [https://github.com/tree-sitter/tree-sitter-ruby](https://github.com/tree-sitter/tree-sitter-ruby) — licensed under
  the MIT License.
- [https://github.com/tree-sitter/tree-sitter-rust](https://github.com/tree-sitter/tree-sitter-rust) — licensed under
  the MIT License.
- [https://github.com/tree-sitter/tree-sitter-typescript](https://github.com/tree-sitter/tree-sitter-typescript) —
  licensed under the MIT License.
