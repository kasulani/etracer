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

    # Enable tracer with AI
    etracer.enable(
        enable_ai=True,
        api_key="your-api-key",
        model="your-preferred-model",
        base_url="https://your-endpoint"
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
    etracer.enable(
        enable_ai=True,
        api_key="your-api-key",
        model="your-preferred-model",
        base_url="https://your-endpoint"
    )

    # All uncaught exceptions will be handled by tracer

2. Function Decorator
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer

    # Configure as needed
    etracer.enable(
        enable_ai=True,
        api_key="your-api-key",
        model="your-preferred-model",
        base_url="https://your-endpoint"
    )

    @etracer.analyze
    def my_function():
        # If this function raises an exception, tracer will handle it
        x = 1 / 0

3. Context Manager
~~~~~~~~~~~~~~~~

.. code-block:: python

    import etracer

    # Configure as needed
    etracer.enable(
        enable_ai=True,
        api_key="your-api-key",
        model="your-preferred-model",
        base_url="https://your-endpoint"
    )

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

    ================================================================================
    ZeroDivisionError: division by zero
    ================================================================================
    Stack Trace: (most recent call last)
    Frame[1/1], file "/Users/emmanuel.kasulani/Projects/etracer/examples.py", line 19, in zero_division
        16:     try:
        17:         x = 10
        18:         y = 0
      > 19:         result = x / y
        20:         print(f"Result: {result}")  # This should not execute

      Local variables:
        x = 10
        y = 0
        e = ZeroDivisionError('division by zero')

    Analyzing error with AI...
    Finished reading from cache 0.00s
    AI Analysis completed in 7.09s
    Caching AI response with key 6b466215770b73fc6da24d3601e9ab4e

    Analysis:
    The error occurs because the code attempts to divide the variable 'x' (which is 10) by 'y' (which is 0). In Python, division by zero is not defined, leading to a ZeroDivisionError. This is a common error when performing arithmetic operations, and it indicates that the denominator in a division operation cannot be zero.

    Suggested Fix:
    To fix this error, you should check if 'y' is zero before performing the division. You can modify the code as follows:

    try:
        x = 10
        y = 0
        if y == 0:
            print("Cannot divide by zero")
        else:
            result = x / y
            print(f"Result: {result}")
    except ZeroDivisionError as e:
        print(f"Error: {e}")

    This way, you avoid the division by zero and handle the situation gracefully.
    ================================================================================
    End of Traceback
    ================================================================================
