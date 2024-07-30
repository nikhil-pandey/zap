# Contributing to Zap ⚡️

We're thrilled that you're interested in contributing to Zap ⚡️! This document provides guidelines for contributing to the project. By participating in this project, you agree to abide by its terms.

## Table of Contents

- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Community](#community)

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```
   git clone https://github.com/your-username/zap.git
   cd zap
   ```
3. Install dependencies:
   ```
   poetry install
   ```
4. Create a branch for your changes:
   ```
   git checkout -b your-branch-name
   ```

## How to Contribute

1. Before making significant changes, please start a discussion:
   - For feature ideas or significant refactoring, [open a discussion on GitHub](https://github.com/nikhil-pandey/zap/discussions).
   - For quick questions or to chat with the community, join our [Discord server](https://discord.gg/jAEuU9KPdx).

2. Once you've gotten feedback, make your changes in your fork.

3. If you've added code that should be tested, add tests.

4. If you've changed APIs, update the documentation.

5. Ensure the test suite passes:
   ```
   poetry run pytest
   ```

6. Make sure your code lints:
   ```
   poetry run flake8
   ```

7. Commit your changes (see [Commit Messages](#commit-messages)).

8. Push to your fork and [submit a pull request](#pull-requests).

9. Wait for the maintainers to review your pull request. They may suggest some changes or improvements or alternatives.

Remember, starting a discussion before making significant changes can save time and effort for both you and the maintainers. It ensures that your contribution aligns with the project's goals and current priorities.

This addition encourages contributors to engage in discussions before making significant changes. It helps to:

1. Align the contributor's ideas with the project's goals
2. Get early feedback from maintainers and the community
3. Prevent duplicate work
4. Build a sense of community around the project

## Style Guidelines

- Follow PEP 8 style guide for Python code.
- Use type hints where applicable.
- Write docstrings for all public modules, functions, classes, and methods.
- Keep line length to a maximum of 120 characters.
- Use meaningful variable names and follow the project's naming conventions.

## Pull Requests

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).

## Reporting Bugs

- Use the issue tracker to report bugs.
- Describe the bug in detail.
- Provide a specific, reproducible scenario.
- Include relevant information such as OS, Python version, and Zap version.

## Suggesting Enhancements

- Use the issue tracker to suggest enhancements.
- Provide a clear and detailed explanation of the feature.
- Explain why this enhancement would be useful to most Zap users.
- List some examples of how this feature would be used.

## Community

- Join our [Discord server](https://discord.gg/jAEuU9KPdx) for discussions.

Thank you for contributing to Zap ⚡️!