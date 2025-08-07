"""
Test script for the tracer module.
Run this script to see how tracer handles different types of exceptions.
"""
import os
import etracer

AI_MODEL = "gpt-4o-mini"


def zero_division():
    """Test handling of ZeroDivisionError"""
    print("\nTesting division by zero...")
    try:
        x = 10
        y = 0
        result = x / y
        print(f"Result: {result}")  # This should not execute
    except Exception as e:
        print("Caught an exception! Using tracer.analyze_exception...")
        etracer.analyze_exception(e)


@etracer.debug
def decorated_function():
    """Test the decorator functionality"""
    print("\nTesting the @etracer.debug decorator...")
    # This will cause a KeyError
    my_dict = {"a": 1, "b": 2}
    value = my_dict["c"]  # This will raise a KeyError
    return value


def context_manager():
    """Test the context manager functionality"""
    print("\nTesting the context manager...")
    with etracer.analyzer():
        # This will cause an AttributeError
        x = 42
        x.append(10)  # integers don't have append method


def global_handler():
    """Test the global exception handler"""
    print("\nTesting the global exception handler...")
    print("This will trigger the global handler and may exit the program")
    print("Comment out this test if you want to run the other tests")

    # Cause a deliberate error that will be caught by the global handler
    undefined_variable = "defined"  # Comment this line out to cause a NameError
    print(undefined_variable + " is now defined")


def main():
    """Main function to run all tests"""
    print("Starting etracer tests...")

    # Enable the tracer with detailed output
    etracer.enable(
        verbosity=2,
        enable_ai=True,
        api_key=os.getenv("OPENAI_API_KEY"),
        model=AI_MODEL,
    )

    # To run any specific test, uncomment the corresponding function call below
    zero_division()
    # decorated_function()
    # context_manager()
    # global_handler()

    print("\nAll tests completed!")


if __name__ == "__main__":
    main()
