import pytest

from zap.git_analyzer.models.enums import Language, PackageManager
from zap.git_analyzer.parsers.dotnet import DotNetParser


@pytest.mark.asyncio
async def test_dotnet_parser(sample_csproj_content):
    parser = DotNetParser()
    result = await parser.parse(sample_csproj_content, "test.csproj")

    assert result.language == Language.CSHARP
    assert result.package_manager == PackageManager.NUGET
    assert "Newtonsoft.Json" in result.dependencies
    assert (
        "ProjectReference:../AnotherProject/AnotherProject.csproj"
        in result.dependencies
    )
    assert len(result.dependencies) == 2
    assert "test.csproj" in result.config_files
