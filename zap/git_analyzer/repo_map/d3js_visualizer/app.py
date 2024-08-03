from flask import Flask, jsonify, send_from_directory, request
import networkx as nx
from pathlib import Path
import asyncio
from zap.git_analyzer.repo_map.code_analyzer import CodeAnalyzer
from zap.git_analyzer.repo_map.repo_map import RepoMap
from zap.git_analyzer.repo_map.codeanalyzerconfig import CodeAnalyzerConfig
from zap.git_analyzer.logger import LOGGER

app = Flask(__name__)

code_analyzer = None


def get_code_analyzer(repo_path=None):
    global code_analyzer
    if code_analyzer is None or repo_path:
        config = CodeAnalyzerConfig(repo_path,
                                    repo_url=repo_path if repo_path and repo_path.startswith(("http://", "https://")) else None)
        if config.root_path or config.repo_url:
            code_analyzer = CodeAnalyzer(config)
            LOGGER.info(f"RepoAnalyzer initialized for {repo_path}")
        else:
            LOGGER.error("No repository URL or file path provided")
    return code_analyzer


@app.route('/analyze')
async def analyze_repo():
    repo_path = request.args.get('repo_path', '')
    if not repo_path:
        LOGGER.error("No repository URL or file path provided")
        return jsonify({'error': 'No repository URL or file path provided'}), 400

    repo_analyzer = get_code_analyzer(repo_path)
    try:
        focus_files = []
        other_files = [str(p) for p in Path(repo_analyzer.config.root_path).rglob("*.py") if p not in focus_files]
        all_files = focus_files + other_files
        if not all_files:
            all_files = [str(p) for p in Path(repo_analyzer.config.root_path).rglob("*.py")]

        file_infos = await repo_analyzer.analyze_files(all_files)
        graph = await repo_analyzer.build_graph(file_infos)
        repo_map = RepoMap(graph, file_infos)

        LOGGER.info(f"Repository {repo_path} analyzed successfully")
        return jsonify({
            'focus_files': [str(p) for p in Path(repo_analyzer.config.root_path).rglob("*.py")]
        })
    except ValueError as e:
        LOGGER.error(f"ValueError: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        LOGGER.error(f"RuntimeError: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/graph')
async def get_graph():
    focus_file = request.args.get('focus_file', '')
    focus_files = focus_file.split(',') if focus_file else []
    mentioned_identifiers = request.args.get('mentioned_identifiers', '')
    mentioned_idents = set(mentioned_identifiers.split(',')) if mentioned_identifiers else set()

    if not focus_files:
        LOGGER.error("No focus files provided")
        return jsonify({'error': 'No focus files provided'}), 400

    repo_analyzer = get_code_analyzer()
    repo_path = repo_analyzer.config.root_path
    other_files = [str(p) for p in Path(repo_path).rglob("*.py") if p not in focus_files]

    all_files = focus_files + other_files
    if not all_files:
        all_files = [str(p) for p in Path(repo_path).rglob("*.py")]

    try:
        file_infos = await repo_analyzer.analyze_files(all_files)
        graph = await repo_analyzer.build_graph(file_infos)

        repo_map = RepoMap(graph, file_infos)
        repo_map.get_ranked_tags_map(focus_files, mentioned_idents, max_files=20, max_tags_per_file=50)

        data = nx.node_link_data(repo_map.nx_graph)
        LOGGER.info("Graph data generated successfully")
        return jsonify(data)
    except ValueError as e:
        LOGGER.error(f"ValueError: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        LOGGER.error(f"RuntimeError: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/focus_files')
async def get_focus_files():
    repo_analyzer = get_code_analyzer()
    if not repo_analyzer:
        LOGGER.error("No repository URL or file path provided")
        return jsonify({'error': 'No repository URL or file path provided'}), 400
    repo_path = repo_analyzer.config.root_path
    all_files = [str(p) for p in Path(repo_path).rglob("*.py")]
    LOGGER.info("Focus files fetched")
    return jsonify(all_files)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HypercornConfig

    config = HypercornConfig()
    config.bind = ["0.0.0.0:5001"]

    LOGGER.info("Starting server")
    asyncio.run(serve(app, config))
