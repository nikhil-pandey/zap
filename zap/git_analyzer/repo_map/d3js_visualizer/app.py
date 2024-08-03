from flask import Flask, jsonify, send_from_directory, request
import networkx as nx
from pathlib import Path
import asyncio
from zap.git_analyzer.repo_map.repo_analyzer import RepoAnalyzer
from zap.git_analyzer.repo_map.repo_map import RepoMap
from zap.git_analyzer.repo_map.config import Config

app = Flask(__name__)

repo_analyzer = None


def get_repo_analyzer():
    global repo_analyzer
    if repo_analyzer is None:
        repo_path = '/Users/nikhilpandey/Projects/zapfinal/zap'  # Update this to your repo path
        config = Config(repo_path)
        repo_analyzer = RepoAnalyzer(config)
    return repo_analyzer


@app.route('/graph')
async def get_graph():
    focus_file = request.args.get('focus_file', '')
    focus_files = focus_file.split(',') if focus_file else []
    mentioned_identifiers = request.args.get('mentioned_identifiers', '')
    mentioned_idents = set(mentioned_identifiers.split(',')) if mentioned_identifiers else set()

    if not focus_files:
        return jsonify({'error': 'No focus files provided'}), 400

    repo_analyzer = get_repo_analyzer()
    repo_path = '/Users/nikhilpandey/Projects/zapfinal/zap'
    other_files = [str(p) for p in Path(repo_path).rglob("*.py") if p not in focus_files]

    all_files = focus_files + other_files
    if not all_files:
        all_files = [str(p) for p in Path(repo_path).rglob("*.py")]

    try:
        file_infos = await repo_analyzer.analyze_files(all_files)
        graph = await repo_analyzer.build_graph(file_infos)

        repo_map = RepoMap(graph, file_infos)
        repo_map.get_ranked_tags_map(focus_files, mentioned_idents, max_files=20, max_tags_per_file=50)

        # Convert the graph to JSON
        data = nx.node_link_data(repo_map.nx_graph)
        return jsonify(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/focus_files')
async def get_focus_files():
    repo_path = '/Users/nikhilpandey/Projects/zapfinal/zap'  # Update this to your repo path
    all_files = [str(p) for p in Path(repo_path).rglob("*.py")]
    return jsonify(all_files)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HypercornConfig

    config = HypercornConfig()
    config.bind = ["0.0.0.0:5001"]

    asyncio.run(serve(app, config))
