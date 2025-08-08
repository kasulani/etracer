"""
etracer: Enhanced Python tracer with AI-powered error analysis
"""

__version__ = "0.1.0"

from .tracer import (
    Tracer,
    enable,
    disable,
    analyze,
    analyzer,
    analyze_exception,
    set_printer,
)

from .models import Frame, DataForAnalysis, AiAnalysis, CacheData
from .interfaces import (
    AnalysisGetterInterface,
    CacheInterface,
    PrinterInterface,
    ProgressIndicatorInterface,
    TimerInterface,
)

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
