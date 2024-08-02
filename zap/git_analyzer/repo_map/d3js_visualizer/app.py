from flask import Flask, jsonify, send_from_directory, request
import networkx as nx
from pathlib import Path
from zap.git_analyzer.repo_map.repo_analyzer import RepoAnalyzer
from zap.git_analyzer.repo_map.repo_map import RepoMap
from zap.git_analyzer.repo_map.config import Config

app = Flask(__name__)


def get_repo_analyzer():
    repo_path = '/Users/nikhilpandey/Projects/zapfinal/zap'  # Update this to your repo path
    config = Config()
    return RepoAnalyzer(repo_path, config)


@app.route('/graph')
def get_graph():
    focus_file = request.args.get('focus_file', '')
    repo_analyzer = get_repo_analyzer()
    repo_path = '/Users/nikhilpandey/Projects/zapfinal/zap'  # Update this to your repo path
    focus_files = [focus_file] if focus_file else []
    other_files = [str(p) for p in Path(repo_path).rglob("*.py") if p not in focus_files]

    all_files = focus_files + other_files
    if not all_files:
        all_files = [str(p) for p in Path(repo_path).rglob("*.py")]

    file_infos = repo_analyzer.analyze_files(all_files)
    graph = repo_analyzer.build_graph(file_infos)

    repo_map = RepoMap(graph, file_infos)

    # Convert the graph to JSON
    data = nx.node_link_data(repo_map.nx_graph)
    return jsonify(data)


@app.route('/focus_files')
def get_focus_files():
    repo_path = '/Users/nikhilpandey/Projects/zapfinal/zap'  # Update this to your repo path
    all_files = [str(p) for p in Path(repo_path).rglob("*.py")]
    return jsonify(all_files)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


if __name__ == "__main__":
    app.run(debug=True)
