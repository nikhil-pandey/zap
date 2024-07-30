# Code Conventions

## General Conventions
- Follow PEP 8 guidelines for Python code.
- Use type hints for function signatures and variable declarations.
- Use `async` and `await` for asynchronous operations.
- Use context managers (`with` statements) for resource management.

## Naming Conventions
- Use `snake_case` for variable and function names.
- Use `PascalCase` for class names.
- Use `UPPER_SNAKE_CASE` for constants.

## Typing Conventions
- For Python 3.9 and above, prefer using built-in generic types like `list` and `dict` instead of `List` and `Dict` from `typing`.

## Dependency Conventions
- Use `poetry` for dependency management.
- For `questionary` prompts, use `ask_async` instead of `ask` for asynchronous operations.

## Testing Conventions
- Make sure code coverage is at least 90%
- Make sure to use temp directories for tests that require file I/O.
- Use `pytest` for testing.
- Use `pytest-asyncio` for testing asynchronous code.
- Use `coverage` for code coverage.