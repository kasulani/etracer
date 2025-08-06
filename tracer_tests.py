"""
Test script for the AI-enhanced tracer module.
This demonstrates how to use the AI-powered error analysis feature.
"""

import tracer
import os

# Configure AI integration (use your own API key)
# You can also set this via environment variable: export OPENAI_API_KEY="your-api-key"
API_KEY = os.environ.get("OPENAI_API_KEY", "")

if API_KEY:
    # Enable tracer with AI integration
    tracer.configure_ai(api_key=API_KEY, model="gpt-3.5-turbo")
    tracer.enable(verbosity=2, show_locals=True, ai_enabled=True)
    print("AI-powered error analysis enabled")
else:
    # Enable tracer without AI
    tracer.enable(verbosity=2, show_locals=True)
    print("AI analysis disabled (no API key provided)")
    print("Set the OPENAI_API_KEY environment variable to enable AI analysis")


@tracer.debug
def test_division_by_zero():
    """Test zero division error with AI analysis"""
    print("Testing division by zero...")
    x = 10
    y = 0
    result = x / y  # This will raise a ZeroDivisionError
    return result


@tracer.debug
def test_attribute_error():
    """Test attribute error with AI analysis"""
    print("Testing attribute error...")
    x = 42  # int doesn't have append method
    x.append(10)  # This will raise an AttributeError
    return x


@tracer.debug
def test_index_error():
    """Test index error with AI analysis"""
    print("Testing index error...")
    my_list = [1, 2, 3]
    value = my_list[10]  # This will raise an IndexError
    return value


def test_with_context_manager():
    """Test error handling with context manager"""
    print("Testing error with context manager...")
    with tracer.catch_errors():
        # This will raise a TypeError
        result = "5" + 5
        print(f"Result: {result}")  # This line won't execute


def main():
    """Run all tests"""
    print("\n1. Testing decorator with division by zero")
    try:
        test_division_by_zero()
    except Exception:
        pass  # Exception is already handled by the decorator

    print("\n2. Testing decorator with attribute error")
    try:
        test_attribute_error()
    except Exception:
        pass  # Exception is already handled by the decorator

    print("\n3. Testing decorator with index error")
    try:
        test_index_error()
    except Exception:
        pass  # Exception is already handled by the decorator

    print("\n4. Testing context manager")
    test_with_context_manager()

    print("\nAll tests completed.")


if __name__ == "__main__":
    main()
