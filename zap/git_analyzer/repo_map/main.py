import sys
from repo_analyzer import RepoAnalyzer
from repo_map import RepoMap
from zap.git_analyzer.repo_map.config import Config


def main(repo_path: str, focus_files: list[str], other_files: list[str], config: Config):
    analyzer = RepoAnalyzer(repo_path, config)

    all_files = focus_files + other_files
    file_infos = analyzer.analyze_files(all_files)
    graph = analyzer.build_graph(file_infos)

    repo_map = RepoMap(graph, file_infos)  # Pass file_infos here
    ranked_tags = repo_map.get_ranked_tags_map(focus_files, config.max_files, config.max_tags_per_file)
    ranked_tags = repo_map.get_ranked_tags_map(focus_files, max_files=20)

    for tag in ranked_tags:
        print(f"{tag.rel_fname}:{tag.line} - {tag.name} ({tag.kind})")


if __name__ == "__main__":
    repo_path = sys.argv[1]
    focus_files = sys.argv[2].split(',')
    other_files = sys.argv[3].split(',') if len(sys.argv) > 3 else []
    main(repo_path, focus_files, other_files, Config())
