import pytest

from zap.git_analyzer.parsers.dotnet import DotNetParser
from zap.git_analyzer.parsers.javascript import JavaScriptParser
from zap.git_analyzer.parsers.python import PythonParser


@pytest.mark.asyncio
async def test_python_parser_edge_cases():
    parser = PythonParser()

    # Test with commented out dependencies
    content = """
    # requests==2.25.1
    numpy==1.20.1
    # pandas
    scipy>=1.6.0
    """
    result = await parser.parse(content, "requirements.txt")
    assert "requests" not in result.dependencies
    assert "numpy" in result.dependencies
    assert "pandas" not in result.dependencies
    assert any(dep.startswith("scipy") for dep in result.dependencies)

    # Test with complex version specifiers
    content = """
    package1~=1.0
    package2>=2.0,<3.0
    package3==1.0.*
    """
    result = await parser.parse(content, "requirements.txt")
    assert all(
        any(dep.startswith(pkg) for dep in result.dependencies)
        for pkg in ["package1", "package2", "package3"]
    )


@pytest.mark.asyncio
async def test_javascript_parser_edge_cases():
    parser = JavaScriptParser()

    # Test with different dependency types
    content = """{
      "dependencies": {
        "package1": "^1.0.0",
        "package2": "~2.0.0",
        "package3": "3.0.0",
        "package4": "git+https://github.com/user/repo.git",
        "package5": "file:../local-package"
      },
      "devDependencies": {
        "dev-package": "latest"
      },
      "peerDependencies": {
        "peer-package": ">=1.0.0"
      }
    }"""
    result = await parser.parse(content, "package.json")
    assert all(
        dep in result.dependencies
        for dep in [
            "package1",
            "package2",
            "package3",
            "package4",
            "package5",
            "dev-package",
            "peer-package",
        ]
    )


@pytest.mark.asyncio
async def test_dotnet_parser_edge_cases():
    parser = DotNetParser()

    # Test with complex project structure and conditional dependencies
    content = """
    <Project Sdk="Microsoft.NET.Sdk">
      <PropertyGroup>
        <TargetFrameworks>netstandard2.0;net5.0</TargetFrameworks>
      </PropertyGroup>
      <ItemGroup>
        <PackageReference Include="Newtonsoft.Json" Version="12.0.3" />
        <PackageReference Include="Serilog" Version="2.10.0" Condition="'$(TargetFramework)' == 'net5.0'" />
      </ItemGroup>
      <ItemGroup Condition="'$(TargetFramework)' == 'netstandard2.0'">
        <PackageReference Include="Microsoft.CSharp" Version="4.7.0" />
      </ItemGroup>
    </Project>
    """
    result = await parser.parse(content, "project.csproj")
    assert "Newtonsoft.Json" in result.dependencies
    assert "Serilog" in result.dependencies
    assert "Microsoft.CSharp" in result.dependencies
