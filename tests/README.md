# 📋 Protonion Jira Agent - Test Suite

## ✅ Test Results

All tests passing! 🎉

```
================= 13 passed in 1.89s =================
```

## 🧪 Running Tests

### Run all tests:
```bash
uv run pytest tests/ -v
```

### Run specific test file:
```bash
uv run pytest tests/test_server.py -v
```

### Run specific test class:
```bash
uv run pytest tests/test_server.py::TestValidators -v
```

### Run with coverage:
```bash
uv run pytest tests/ --cov=src --cov-report=html
```

## 📦 Test Coverage

### Validators (100%)
- ✅ `validate_issue_key()` - Valid and invalid formats
- ✅ `validate_status()` - Valid and invalid statuses  
- ✅ `validate_board_id()` - Valid and invalid IDs
- ✅ `validate_limit()` - Valid and invalid limits

### Caching (100%)
- ✅ TTL Cache - Set, get, expiration
- ✅ Cache decorator functionality

### Health Check (100%)
- ✅ Healthy status
- ✅ Unhealthy status
- ✅ Report formatting

## 🔄 Continuous Integration

Add this to your CI/CD pipeline:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run tests
        run: uv run pytest tests/ -v
```

## 📝 Writing New Tests

### Example: Testing a new validator

```python
def test_validate_custom_field():
    """Test custom field validation"""
    from src.jira_tools.validators import validate_custom_field
    
    # Valid cases
    assert validate_custom_field("CF-123") == "CF-123"
    
    # Invalid cases
    with pytest.raises(ValidationError):
        validate_custom_field("invalid")
```

### Example: Testing with mocks

```python
from unittest.mock import Mock, patch

def test_with_mock_client():
    """Test with mocked Jira client"""
    with patch('src.jira_tools.client.JiraClient') as mock_client:
        mock_client.return_value.current_user.return_value = "test_user"
        
        # Your test logic here
        result = some_function()
        assert result == expected_value
```

## 🐛 Debugging Failed Tests

### View detailed output:
```bash
uv run pytest tests/ -vv
```

### Stop on first failure:
```bash
uv run pytest tests/ -x
```

### Run last failed tests:
```bash
uv run pytest tests/ --lf
```

### Enter debugger on failure:
```bash
uv run pytest tests/ --pdb
```
