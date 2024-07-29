import asyncio
import os

import pytest

from zap.git_analyzer.repo.git_repo import GitRepo


@pytest.mark.asyncio
async def test_git_repo_initialization(temp_git_repo):
    assert isinstance(temp_git_repo, GitRepo)
    assert os.path.exists(temp_git_repo.path)


@pytest.mark.asyncio
async def test_get_tracked_files(temp_git_repo):
    # Create a file and add it to git
    with open('test_file.txt', 'w') as f:
        f.write('Test content')
    await asyncio.to_thread(os.system, 'git add test_file.txt')
    await asyncio.to_thread(os.system, 'git commit -m "Add test file"')

    tracked_files = await temp_git_repo.get_tracked_files()
    assert 'test_file.txt' in tracked_files


@pytest.mark.asyncio
async def test_get_file_content(temp_git_repo):
    # Create a file with known content
    with open('content_file.txt', 'w') as f:
        f.write('File content for testing')
    await asyncio.to_thread(os.system, 'git add content_file.txt')
    await asyncio.to_thread(os.system, 'git commit -m "Add content file"')

    content = await temp_git_repo.get_file_content('content_file.txt')
    assert content == 'File content for testing'


@pytest.mark.asyncio
async def test_get_status(temp_git_repo):
    # Create and add a file
    with open('test_file.txt', 'w') as f:
        f.write('Initial content')
    await asyncio.to_thread(os.system, 'git add test_file.txt')
    await asyncio.to_thread(os.system, 'git commit -m "Add test file"')

    # Create a new file
    with open('new_file.txt', 'w') as f:
        f.write('New file content')

    # Modify the existing file
    with open('test_file.txt', 'a') as f:
        f.write('Modified content')

    status = await temp_git_repo.get_status()
    assert 'new_file.txt' in status['new']
    assert 'test_file.txt' in status['modified']


@pytest.mark.asyncio
async def test_get_recent_commits_empty_repo(temp_git_repo):
    commits = await temp_git_repo.get_recent_commits()
    assert len(commits) == 0


@pytest.mark.asyncio
async def test_get_recent_commits_with_commits(temp_git_repo):
    # Create some commits
    for i in range(5):
        with open(f'file_{i}.txt', 'w') as f:
            f.write(f'Content {i}')
        await asyncio.to_thread(os.system, f'git add file_{i}.txt')
        await asyncio.to_thread(os.system, f'git commit -m "Commit {i}"')

    commits = await temp_git_repo.get_recent_commits(3)
    assert len(commits) == 3
    assert all(hasattr(commit, 'hash') for commit in commits)
    assert all(hasattr(commit, 'message') for commit in commits)
    assert all(hasattr(commit, 'author') for commit in commits)
    assert all(hasattr(commit, 'time') for commit in commits)


@pytest.mark.asyncio
async def test_get_file_change_count_empty_repo(temp_git_repo):
    file_change_count = await temp_git_repo.get_file_change_count()
    assert len(file_change_count) == 0


@pytest.mark.asyncio
async def test_get_file_change_count(temp_git_repo):
    # Create some files and make commits
    for i in range(3):
        with open(f'file_{i}.txt', 'w') as f:
            f.write(f'Content {i}')
        await asyncio.to_thread(os.system, f'git add file_{i}.txt')
        await asyncio.to_thread(os.system, f'git commit -m "Add file_{i}.txt"')

    # Modify file_0.txt
    with open('file_0.txt', 'a') as f:
        f.write('More content')
    await asyncio.to_thread(os.system, 'git add file_0.txt')
    await asyncio.to_thread(os.system, 'git commit -m "Update file_0.txt"')

    file_change_count = await temp_git_repo.get_file_change_count()

    assert file_change_count['file_0.txt'] == 2
    assert file_change_count['file_1.txt'] == 1
    assert file_change_count['file_2.txt'] == 1
