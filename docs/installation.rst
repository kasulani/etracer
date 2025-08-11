Installation
============

Requirements
-----------

- Python 3.8+
- pydantic 2.0+
- openai 1.99.6+

Installing from PyPI (future)
----------------------------

.. code-block:: bash

    pip install etracer

Installing from GitHub
--------------------

.. code-block:: bash

    # Install directly from the repository
    pip install git+https://github.com/emmanuelkasulani/etracer.git

    # For development, clone the repository and install in editable mode
    git clone https://github.com/emmanuelkasulani/etracer.git
    cd etracer
    pip install -e .

Development Installation
----------------------

To install etracer with development dependencies:

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/emmanuelkasulani/etracer.git
    cd etracer

    # Install development dependencies
    pip install -e ".[dev]"
