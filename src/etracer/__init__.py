"""
eTracer: An enhanced Python tracer

:copyright: 2025, Emmanuel King Kasulani
:license: Apache License 2.0, see LICENSE for more details.

A utility package that provides enhanced debugging for Python stack traces.
It hijacks the default exception handling process to provide clearer,
more readable stack traces with AI-powered explanations and suggested fixes.
"""

__version__ = "0.1.0"

from .interfaces import (
    AnalysisGetterInterface,
    CacheInterface,
    PrinterInterface,
    ProgressIndicatorInterface,
    TimerInterface,
)
from .models import AiAnalysis, CacheData, DataForAnalysis, Frame
from .tracer import Tracer, analyze, analyze_exception, analyzer, disable, enable, set_printer

__all__ = [
    "Tracer",
    "enable",
    "disable",
    "analyze",
    "analyzer",
    "analyze_exception",
    "set_printer",
    "Frame",
    "DataForAnalysis",
    "AiAnalysis",
    "CacheData",
    "AnalysisGetterInterface",
    "CacheInterface",
    "PrinterInterface",
    "ProgressIndicatorInterface",
    "TimerInterface",
]
