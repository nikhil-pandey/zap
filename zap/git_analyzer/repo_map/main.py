import sys
from pathlib import Path

from repo_analyzer import RepoAnalyzer
from repo_map import RepoMap
from zap.git_analyzer.repo_map.config import Config


def main(repo_path: str, focus_files: list[str], other_files: list[str], config: Config):
    analyzer = RepoAnalyzer(repo_path, config)

    all_files = focus_files + other_files
    file_infos = analyzer.analyze_files(all_files)
    graph = analyzer.build_graph(file_infos)

    repo_map = RepoMap(graph, file_infos)  # Pass file_infos here
    ranked_tags = repo_map.get_ranked_tags_map(focus_files, {}, config.max_files, config.max_tags_per_file)

    print("Ranked tags:")
    for tag in ranked_tags:
        print(f"{tag.path}:{tag.line} - {tag.name} ({tag.kind})")

    symbol = "initialize"
    tags = analyzer.query_symbol(symbol)
    print("\nFound tags:")
    for tag in tags:
        print(f"Found symbol '{symbol}' in {tag.path} at line {tag.line}, {tag.body}")


if __name__ == "__main__":
    repo_path = sys.argv[1]
    focus_files = sys.argv[2].split(',')
    other_files = sys.argv[3].split(',') if len(sys.argv) > 3 else []
    if not other_files:
        other_files = [str(p) for p in Path(repo_path).rglob("*.py")]
    main(repo_path, focus_files, other_files, Config())
