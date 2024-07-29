import logging
import os
import shutil
import tempfile
import time
from contextlib import contextmanager

import pytest

from zap.git_analyzer.repo.git_repo import GitRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def safe_temp_dir():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        retry_count = 5
        while retry_count > 0:
            try:
                shutil.rmtree(temp_dir)
                break
            except PermissionError as e:
                logger.warning(f"Failed to remove temp directory: {e}. Retrying in 1 second...")
                time.sleep(1)
                retry_count -= 1
        if retry_count == 0:
            logger.error(f"Failed to remove temp directory after multiple attempts: {temp_dir}")


@pytest.fixture
def temp_git_repo():
    with safe_temp_dir() as tmp_dir_name:
        original_dir = os.getcwd()
        os.chdir(tmp_dir_name)
        os.system('git init')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        repo = GitRepo(tmp_dir_name)
        try:
            yield repo
        finally:
            repo.close()
            os.chdir(original_dir)


@pytest.fixture
def sample_csproj_content():
    return '''
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="12.0.3" />
    <ProjectReference Include="..\AnotherProject\AnotherProject.csproj" />
  </ItemGroup>
</Project>
'''


@pytest.fixture
def sample_requirements_txt_content():
    return '''
requests==2.25.1
pytest==6.2.3
'''


@pytest.fixture
def sample_package_json_content():
    return '''{
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^26.6.3"
  }
}'''
