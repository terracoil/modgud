"""
Result monad types for error handling.

This sub-package contains the Result monad implementation with
Ok and Err types for functional error handling patterns.
"""

from ...domain.result_protocol import ResultProtocol as Result
from .err_result import Err
from .ok_result import Ok

__all__ = [
  'Result',
  'Ok',
  'Err',
]
