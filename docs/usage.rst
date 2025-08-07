Usage
=====

Quick Start
----------

Basic Usage (No AI)
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer

    # Enable tracer at the start of your script
    etracer.enable()

    # Your code here
    # Any uncaught exceptions will be processed by tracer

With AI-Powered Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer
    import os

    # Enable tracer with AI (using environment variable for API key)
    API_KEY = os.environ.get("OPENAI_API_KEY")
    etracer.enable(
        enable_ai=True,
        api_key=API_KEY,
        model="gpt-3.5-turbo"
    )

    # Your code here
    # Errors will now get AI-powered explanations and fixes

Usage Modes
-----------

1. Global Exception Handler
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer

    # Enable at the start of your script
    etracer.enable(verbosity=2, show_locals=True, enable_ai=True)

    # All uncaught exceptions will be handled by tracer

2. Function Decorator
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer

    # Configure as needed
    etracer.enable()

    @etracer.debug
    def my_function():
        # If this function raises an exception, tracer will handle it
        x = 1 / 0

3. Context Manager
~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer

    # Configure as needed
    etracer.enable()

    # Use context manager for specific code blocks
    with etracer.analyzer():
        # Only exceptions in this block will be handled by tracer
        result = "5" + 5  # TypeError

4. Explicit Analysis
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer

    # Configure as needed
    etracer.enable(
        enable_ai=True,
        api_key="your-api-key",
        model="your-preferred-model",
        base_url="https://your-endpoint"
    )

    try:
        x = 10
        y = 0
        result = x / y
    except Exception as e:
        # Explicitly analyze this exception
        etracer.analyze_exception(e)

Configuration Options
-------------------

.. code-block:: python

    # Basic configuration
    etracer.enable(
        enable_ai=True,
        api_key="your-api-key",
        model="your-preferred-model",
        base_url="https://your-endpoint"
    )

Example Output
------------

.. code-block:: 

    ========================================================================
    ZeroDivisionError: division by zero
    ========================================================================

    Stack Trace: (most recent call last)

    [1/1] File "example.py", line 10, in test_function
    line 8:     x = 10
    line 9:     y = 0
      > 10:     result = x / y
    line 11:     return result
    line 12: 

    Local variables:
        x = 10
        y = 0

    Analysis:
    You attempted to divide by zero, which is a mathematical error. In this case, 
    the variable 'y' has a value of 0, and you're trying to divide 'x' (which is 10) 
    by 'y'. Division by zero is not allowed in mathematics or programming.

    Suggested Fix:
    Add a check to prevent division by zero:

    if y != 0:
        result = x / y
    else:
        result = 0  # or some other fallback value, or raise a custom exception