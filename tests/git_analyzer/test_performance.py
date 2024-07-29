import os
import time

import psutil
import pytest

from zap.git_analyzer import GitAnalyzer
from zap.git_analyzer.config import GitAnalyzerConfig


def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


@pytest.fixture
def large_repo(temp_git_repo):
    # Create a large repository with many files and commits
    for i in range(1000):  # Create 1000 files
        with open(os.path.join(temp_git_repo.path, f'file_{i}.txt'), 'w') as f:
            f.write(f'Content of file {i}\n' * 100)  # Each file has 100 lines

    os.chdir(temp_git_repo.path)
    os.system('git add .')
    for i in range(100):  # Create 100 commits
        os.system(f'git commit -m "Commit {i}"')

    return temp_git_repo


@pytest.fixture
def very_large_repo(temp_git_repo):
    # Create a very large repository (approximately 1GB)
    chunk_size = 1024 * 1024  # 1MB
    num_files = 1000
    content = 'x' * chunk_size

    for i in range(num_files):
        with open(os.path.join(temp_git_repo.path, f'large_file_{i}.txt'), 'w') as f:
            f.write(content)

    os.chdir(temp_git_repo.path)
    os.system('git add .')
    os.system('git commit -m "Add large files"')

    # print the folder size
    size = sum(os.path.getsize(os.path.join(dirpath, filename))
               for dirpath, dirnames, filenames in os.walk(temp_git_repo.path)
               for filename in filenames) / (1024 * 1024)
    print(f"Folder size: {size:.2f} MB")
    return temp_git_repo


@pytest.mark.asyncio
async def test_performance_large_repo(large_repo):
    analyzer = GitAnalyzer(large_repo.path)

    start_time = time.time()
    start_memory = get_process_memory()

    await analyzer.analyze()

    end_time = time.time()
    end_memory = get_process_memory()

    execution_time = end_time - start_time
    memory_used = end_memory - start_memory

    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Memory used: {memory_used / (1024 * 1024):.2f} MB")

    assert execution_time < 60  # Assuming it should complete within 60 seconds
    assert memory_used < 500 * 1024 * 1024  # Assuming it should use less than 500 MB of additional memory


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.large_data
async def test_performance_very_large_repo(very_large_repo):
    analyzer = GitAnalyzer(very_large_repo.path)

    start_time = time.time()
    start_memory = get_process_memory()

    await analyzer.analyze()

    end_time = time.time()
    end_memory = get_process_memory()

    execution_time = end_time - start_time
    memory_used = end_memory - start_memory

    print(f"Execution time for very large repo: {execution_time:.2f} seconds")
    print(f"Memory used for very large repo: {memory_used / (1024 * 1024):.2f} MB")

    assert execution_time < 300  # Assuming it should complete within 5 minutes
    assert memory_used < 2 * 1024 * 1024 * 1024  # Assuming it should use less than 2 GB of additional memory


@pytest.mark.asyncio
async def test_performance_multiple_analyses(large_repo):
    config = GitAnalyzerConfig()
    analyzer = GitAnalyzer(large_repo.path, config)

    start_time = time.time()
    start_memory = get_process_memory()

    for _ in range(5):  # Perform 5 consecutive analyses
        await analyzer.analyze()

    end_time = time.time()
    end_memory = get_process_memory()

    execution_time = end_time - start_time
    memory_used = end_memory - start_memory

    print(f"Execution time for 5 analyses: {execution_time:.2f} seconds")
    print(f"Memory used for 5 analyses: {memory_used / (1024 * 1024):.2f} MB")

    assert execution_time < 300  # Assuming it should complete within 5 minutes
    assert memory_used < 1000 * 1024 * 1024  # Assuming it should use less than 1 GB of additional memory
