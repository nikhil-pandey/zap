import os

import pytest

from zap.git_analyzer.repo.git_repo import GitRepo


@pytest.fixture
def sample_repo(temp_git_repo):
    # Create a sample repository structure
    files = [
        'src/main.py',
        'src/lib/utils.py',
        'docs/readme.md',
        'tests/test_main.py',
        'setup.py',
    ]

    for file_path in files:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(os.path.join(temp_git_repo.path, dir_path), exist_ok=True)
        with open(os.path.join(temp_git_repo.path, file_path), 'w') as f:
            f.write("# Sample content")

    os.chdir(temp_git_repo.path)
    os.system('git add .')
    os.system('git commit -m "Initial commit"')

    return temp_git_repo


@pytest.mark.asyncio
async def test_file_trie(sample_repo):
    repo = GitRepo(sample_repo.path)
    await repo.refresh()
    assert 'src/main.py' in repo.file_trie
    assert 'src/lib/utils.py' in repo.file_trie
    assert 'docs/readme.md' in repo.file_trie
    assert 'tests/test_main.py' in repo.file_trie
    assert 'setup.py' in repo.file_trie


@pytest.mark.asyncio
async def test_suffix_trie(sample_repo):
    repo = GitRepo(sample_repo.path)
    await repo.refresh()
    assert 'main.py/src' in repo.suffix_trie
    assert 'utils.py/lib/src' in repo.suffix_trie
    assert 'readme.md/docs' in repo.suffix_trie
    assert 'test_main.py/tests' in repo.suffix_trie
    assert 'setup.py' in repo.suffix_trie


@pytest.mark.asyncio
async def test_suffix_query(sample_repo):
    repo = GitRepo(sample_repo.path)
    await repo.refresh()
    suffix_query = 'main.py'
    matched_files = [repo.suffix_trie[suffix_key] for suffix_key in repo.suffix_trie.keys() if
                     suffix_key.startswith(suffix_query)]
    assert len(matched_files) == 1
    assert matched_files[0] == 'src/main.py'
