from enum import Enum


class Language(Enum):
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    CSHARP = "C#"
    UNKNOWN = "Unknown"


class PackageManager(Enum):
    PIPENV = "Pipenv"
    PIP = "pip"
    POETRY = "Poetry"
    NPM = "npm"
    NUGET = "NuGet"
    UNKNOWN = "Unknown"


class DependencyFileType(Enum):
    REQUIREMENTS_TXT = "requirements.txt"
    PYPROJECT_TOML = "pyproject.toml"
    PACKAGE_JSON = "package.json"
    CSPROJ = ".csproj"
    PIPFILE = "Pipfile"
