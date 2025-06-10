# Contributing to langchain-naver-community

We welcome contributions to the langchain-naver-community project! This document provides guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Python >= 3.8
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/langchain-naver-community.git
   cd langchain-naver-community
   ```

## Development Setup

### Using uv (Recommended)

```bash
# Install the project in development mode with test dependencies
uv sync --extra test
```

### Using pip

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the project in development mode with test dependencies
pip install -e ".[test]"
```

### Environment Variables

For testing and development, you'll need Naver API credentials:

```bash
export NAVER_CLIENT_ID="your-client-id"
export NAVER_CLIENT_SECRET="your-client-secret"
```

Get your credentials from [Naver Developers](https://developers.naver.com/).

## Code Style

### Python Code Style

- Follow [PEP 8](https://pep8.org/) Python style guidelines
- Use type hints for all function parameters and return values
- Write clear, descriptive docstrings for all classes and functions
- Keep line length under 88 characters (Black formatter default)

### Example Code Style

```python
from typing import Dict, List, Optional

def process_search_results(
    results: List[Dict], 
    max_items: Optional[int] = None
) -> List[Dict]:
    """Process and clean search results from Naver API.
    
    Args:
        results: Raw search results from the API
        max_items: Maximum number of items to return
        
    Returns:
        List of cleaned search result dictionaries
    """
    # Implementation here
    pass
```

### Import Organization

Organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import json
from typing import Dict, List

import aiohttp
from langchain_core.tools import BaseTool

from langchain_naver_community.utils import NaverSearchAPIWrapper
```

## Testing

We use pytest for testing. All contributions should include appropriate tests.

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=langchain_naver_community

# Run specific test file
pytest tests/test_tool.py

# Run with verbose output
pytest -v tests/
```

### Writing Tests

- Write tests for all new functionality
- Include both positive and negative test cases
- Use descriptive test names that explain what is being tested
- Mock external API calls to avoid dependencies on external services

### Test Structure

```python
import pytest
from unittest.mock import Mock

from langchain_naver_community.tool import NaverSearchResults


class TestNaverSearchResults:
    """Test cases for NaverSearchResults tool."""
    
    @pytest.fixture
    def search_tool(self):
        """Create a NaverSearchResults instance for testing."""
        return NaverSearchResults()
    
    def test_initialization(self, search_tool):
        """Test that the tool initializes correctly."""
        assert search_tool.name == "naver_search_results_json"
        assert search_tool.search_type == "news"
```

## Submitting Changes

### Before Submitting

1. **Run tests**: Ensure all tests pass
   ```bash
   pytest tests/
   ```

2. **Check code style**: Follow the style guidelines above

3. **Update documentation**: Update docstrings and README if needed

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**: Implement your feature or fix

3. **Add tests**: Write tests for your changes

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new search functionality"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**: Open a PR on GitHub with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference to any related issues
   - Screenshots or examples if applicable

### Commit Message Guidelines

Use conventional commit format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding tests
- `refactor:` for code refactoring

Examples:
```
feat: add book search functionality
fix: handle API rate limiting properly
docs: update installation instructions
test: add tests for async search methods
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Environment details**: Python version, OS, dependency versions
- **Steps to reproduce**: Clear steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Error messages**: Full error messages and stack traces
- **Code example**: Minimal code example that reproduces the issue

### Feature Requests

For feature requests, please include:

- **Use case**: Describe the problem you're trying to solve
- **Proposed solution**: Your idea for how to solve it
- **Alternatives**: Other solutions you've considered
- **Examples**: Code examples of how the feature would be used

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Spam or off-topic discussions
- Sharing private information without permission

## Development Guidelines

### Adding New Search Types

To add a new search type:

1. **Add to SEARCH_TYPE_MAP** in `utils.py`:
   ```python
   SEARCH_TYPE_MAP = {
       "news": "news",
       "blog": "blog",
       "webkr": "webkr",
       "book": "book",
       "your_new_type": "api_endpoint_name",
   }
   ```

2. **Create a specialized tool class** in `tool.py`:
   ```python
   class NaverYourTypeSearch(NaverSearchResults):
       """Tool specialized for Naver YourType search."""
       
       name: str = "naver_your_type_search"
       description: str = "Description of your search type"
       search_type: str = "your_new_type"
   ```

3. **Add tests** for the new functionality

### API Wrapper Changes

When modifying the `NaverSearchAPIWrapper`:

- Maintain backward compatibility
- Add appropriate error handling
- Update both sync and async methods
- Add comprehensive tests

### Documentation Updates

- Keep docstrings up to date
- Update README.md for user-facing changes
- Add examples for new features
- Update type hints

## Release Process

Releases are handled by maintainers, but contributors should:

- Follow semantic versioning principles
- Update version in `pyproject.toml` if needed
- Document breaking changes clearly
- Ensure all tests pass

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Maintainers will review PRs and provide feedback

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation

Thank you for contributing to langchain-naver-community!