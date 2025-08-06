from pydantic import BaseModel
from typing import Any, Dict, List, Tuple


# Models
class Frame(BaseModel):
    """Model for a single traceback frame."""
    filename: str
    lineno: int
    function: str
    lines: List[Tuple[int, str]]  # List of tuples (line number, line content)
    code_snippet: str  # Code snippet for the frame
    locals: Dict[str, Any]  # Local variables in the frame


class DataForAnalysis(BaseModel):
    """Model for structured error data to be sent for AI analysis."""
    exception_type: str
    exception_message: str
    frames: List[Frame]
    most_relevant_frame: Frame


class AiAnalysis(BaseModel):
    """Model for AI analysis response."""
    explanation: str
    suggested_fix: str


class CacheData(BaseModel):
    """Model for cached AI analysis data."""
    timestamp: float  # Timestamp when the data was cached
    explanation: str  # Explanation provided by AI
    suggested_fix: str  # Suggested fix provided by AI
