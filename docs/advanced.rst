Advanced Usage
=============

Caching System
-------------

eTracer includes a caching system for AI-powered analysis to reduce API costs and improve performance:

- **Cache Location**: A ``.tracer_cache`` directory in your project's root folder
- **What's Cached**: AI responses for specific error patterns to avoid redundant API calls
- **When Used**: Automatically used when the same error occurs multiple times
- **Manual Cleanup**: Simply delete the ``.tracer_cache`` directory to clear the cache

.. code-block:: bash

    # To manually clear the cache:
    rm -rf .tracer_cache

Future Cache Management
~~~~~~~~~~~~~~~~~~~~~

Future versions will include more advanced cache management features such as automatic pruning to keep the cache size manageable. These features will help maintain optimal performance and disk usage over extended periods of development.

AI Integration
------------

eTracer uses the OpenAI client library to connect to AI models that support the OpenAI API format. This means it's compatible with:

- OpenAI models (GPT-3.5, GPT-4, etc.)
- Compatible third-party services that implement the OpenAI API (Anthropic Claude, Cohere, etc.)
- Self-hosted models with OpenAI-compatible APIs (LM Studio, Ollama, etc.)

By default, etracer uses the OpenAI URL ``https://api.openai.com/v1`` as base URL and ``gpt-3.5-turbo`` as the default model. To use a different provider (base URL and model), update the configuration in your code:

.. code-block:: python

    # For using Azure OpenAI
    etracer.enable(
        enable_ai=True,
        api_key="your-api-key",
        model="your-preferred-model",
        base_url="https://your-endpoint"
    )

Customizing Output
----------------

You can customize how etracer displays output by creating your own printer implementation that follows the PrinterInterface:

.. code-block:: python

    from etracer import set_printer
    from etracer.interfaces import PrinterInterface
    
    class MyCustomPrinter(PrinterInterface):
        def __init__(self, verbosity=2):
            self.verbosity = verbosity
            
        def print(self, message, min_verbosity=0):
            if self.verbosity >= min_verbosity:
                # Custom printing logic here
                print(f"[CUSTOM] {message}")
                
        def set_verbosity(self, verbosity):
            self.verbosity = verbosity
    
    # Set your custom printer
    set_printer(MyCustomPrinter())