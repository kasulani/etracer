"""
etracer: Enhanced Python tracer with AI-powered error analysis
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
