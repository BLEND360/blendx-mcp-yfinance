# Tests

This directory contains tests for the MCP tool template. The current tests are **dummy examples** that demonstrate the testing structure. You should replace these with tests for your actual tools.

## Test Structure

- `test_mcp_server.py` - Tests for the MCP server tools and functionality

## Running Tests

### Manual Test Run
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python -m pytest tests/test_mcp_server.py::TestMCPServer::test_example_tool -v
```

## Creating Your Own Tests

### 1. Replace Dummy Tests with Real Tests

The current tests are examples using dummy tools (`example_tool`, `text_analyzer`, etc.). Replace these with tests for your actual tools.

### 2. Required Test Structure

Every MCP tool should have these test types:

#### A. Tool Functionality Tests
Test your tool with valid inputs and expected outputs:

```python
@pytest.mark.asyncio
async def test_your_tool_name(self):
    """Test your tool with valid input."""
    from mcp_server import your_tool_name
    
    # Test with valid input
    result = await your_tool_name("valid input")
    result_data = json.loads(result)
    
    # Assert expected behavior
    assert "expected_field" in result_data
    assert result_data["expected_field"] == "expected_value"
    assert result_data["status"] == "success"
```

#### B. Error Handling Tests
Test your tool with invalid inputs:

```python
@pytest.mark.asyncio
async def test_your_tool_name_empty_input(self):
    """Test your tool with empty/invalid input."""
    from mcp_server import your_tool_name
    
    result = await your_tool_name("")
    result_data = json.loads(result)
    
    assert "error" in result_data
    assert "cannot be empty" in result_data["error"]
```

#### C. Edge Case Tests
Test boundary conditions and edge cases:

```python
@pytest.mark.asyncio
async def test_your_tool_name_edge_cases(self):
    """Test your tool with edge cases."""
    from mcp_server import your_tool_name
    
    # Test with very large input
    large_input = "x" * 10000
    result = await your_tool_name(large_input)
    result_data = json.loads(result)
    
    # Should handle gracefully
    assert "error" not in result_data
```

### 3. Server Configuration Tests (REQUIRED)

These tests ensure your tools are properly registered and documented. **Keep these tests as-is** and just update the expected tool names:

```python
def test_mcp_server_initialization(self):
    """Test that the MCP server is properly initialized."""
    # Check that tools are registered
    tools = list(mcp._tool_manager._tools.keys())
    expected_tools = [
        "your_tool_1",
        "your_tool_2", 
        "your_tool_3",
        # Add all your actual tool names here
    ]
    
    for tool in expected_tools:
        assert tool in tools

def test_mcp_server_tool_descriptions(self):
    """Test that tools have proper descriptions."""
    for tool_name, tool in mcp._tool_manager._tools.items():
        assert hasattr(tool, 'description') or hasattr(tool, '__doc__')
        # Check if tool has either a description attribute or docstring
        if hasattr(tool, 'description'):
            assert tool.description is not None
            assert len(tool.description) > 0
        elif hasattr(tool, '__doc__'):
            assert tool.__doc__ is not None
            assert len(tool.__doc__) > 0
```

## Test Configuration

The tests use:
- `pytest` for test framework
- `pytest-asyncio` for async test support
- `pytest-cov` for coverage reporting

Configuration is in `pytest.ini` at the project root.

## Example: Converting Dummy Tests to Real Tests

### Before (Dummy Test):
```python
@pytest.mark.asyncio
async def test_example_tool(self):
    """Test the example tool function."""
    from mcp_server import example_tool
    
    result = await example_tool("test input")
    result_data = json.loads(result)
    
    assert "processed_input" in result_data
    assert result_data["processed_input"] == "Processed: TEST INPUT"
```

### After (Real Test):
```python
@pytest.mark.asyncio
async def test_data_analyzer(self):
    """Test the data analyzer tool."""
    from mcp_server import data_analyzer
    
    # Test with real data
    test_data = [1, 2, 3, 4, 5]
    result = await data_analyzer(test_data, "mean")
    result_data = json.loads(result)
    
    # Assert real business logic
    assert "mean_value" in result_data
    assert result_data["mean_value"] == 3.0
    assert "data_points" in result_data
    assert result_data["data_points"] == 5
```

## Best Practices

1. **Test Real Functionality**: Don't just test that functions return JSON - test the actual business logic
2. **Test Error Conditions**: Always test what happens with invalid inputs
3. **Test Edge Cases**: Test with empty data, very large data, special characters, etc.
4. **Use Descriptive Names**: Test function names should clearly describe what they test
5. **Assert Meaningful Results**: Don't just check that fields exist - check that they have correct values
6. **Test Async Properly**: Always use `@pytest.mark.asyncio` for async test functions

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the `src` directory is in the Python path
2. **Async Test Failures**: Ensure `@pytest.mark.asyncio` decorator is used for async tests
3. **Tool Access Errors**: Use `mcp._tool_manager._tools` to access registered tools
4. **Test Data Issues**: Use realistic test data that matches your tool's expected input format

### Debug Mode

Run tests with more verbose output:
```bash
python -m pytest tests/ -v -s --tb=long
```

## Reccomendations

**Always include these tests in your final implementation:**
- Server initialization test (verifies all tools are registered)
- Tool descriptions test (ensures proper documentation)
- At least one functionality test per tool
- At least one error handling test per tool 