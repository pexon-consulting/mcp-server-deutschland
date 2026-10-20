"""Write, read and check files in the DATEV-Format (EXTF), category Buchungsstapel.

The core library has no MCP dependency at import time; the MCP server lives in
`extf_buchungsstapel_mcp.server`.
"""

from .columns import BOOKING_COLUMNS_V12, BOOKING_COLUMNS_V13, HEADER_FIELDS
from .codes import CODES
from .explain import explain
from .importer import InputError, load_csv, load_json
from .model import Booking, ExtfValidationError, Finding, Header, Report
from .reader import read_extf, row_to_booking_dict
from .writer import build_extf, validate

__version__ = "0.1.0"

__all__ = [
    "BOOKING_COLUMNS_V12",
    "BOOKING_COLUMNS_V13",
    "CODES",
    "HEADER_FIELDS",
    "Booking",
    "ExtfValidationError",
    "Finding",
    "Header",
    "InputError",
    "Report",
    "__version__",
    "build_extf",
    "explain",
    "load_csv",
    "load_json",
    "read_extf",
    "row_to_booking_dict",
    "validate",
]
