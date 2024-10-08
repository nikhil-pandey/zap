import sys
from pathlib import Path
import asyncio

from code_analyzer import CodeAnalyzer
from repo_map import RepoMap
from zap.git_analyzer.repo_map.codeanalyzerconfig import CodeAnalyzerConfig


async def main(config: CodeAnalyzerConfig, focus_files: list[str], other_files: list[str]):
    analyzer = CodeAnalyzer(config)

    all_files = focus_files + other_files
    file_infos = await analyzer.analyze_files(all_files)
    graph = await analyzer.build_graph(file_infos)

    repo_map = RepoMap(graph, file_infos)  # Pass file_infos here
    ranked_tags = repo_map.get_ranked_tags_map(focus_files, set(), 10, 100)

    print("Ranked tags:")
    for tag in ranked_tags:
        print(f"{tag.path}:{tag.start_line} - {tag.name} ({tag.kind})")

    # Example of querying symbol after building the index
    symbol = "initialize"
    tags = await analyzer.query_symbol(symbol)
    print("\nFound tags:")
    for tag in tags:
        print(f"Found symbol '{symbol}' in {tag.path} at line {tag.start_line}, {tag.body}")


if __name__ == "__main__":
    repo_path = sys.argv[1]
    focus_files = sys.argv[2].split(',')
    other_files = sys.argv[3].split(',') if len(sys.argv) > 3 else []
    if not other_files:
        other_files = [str(p) for p in Path(repo_path).rglob("*.py")]
    asyncio.run(main(CodeAnalyzerConfig(repo_path), focus_files, other_files))
