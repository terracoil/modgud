"""
Result monad types for error handling.

This sub-package contains the Result monad implementation with
Ok and Err types for functional error handling patterns.
"""

from .err_result import Err
from .ok_result import Ok
from ...domain.result_protocol import ResultProtocol as Result

__all__ = [
  'Result',
  'Ok',
  'Err',
]
