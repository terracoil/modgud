"""
Consolidated guards module providing backward compatibility.

Re-exports all guard functions from focused modules while maintaining
the original CommonGuards interface for backward compatibility.
"""

# Import all guard functions from focused modules
from .basic import not_none, not_empty, type_check
from .numeric import positive, negative, in_range
from .string import length, matches_pattern
from .validators import valid_email, valid_url, valid_uuid, valid_file_path
from .combinators import all_of, any_of, custom
from .enum_guard import valid_enum
from .base import extract_param


class CommonGuards:
  """
  Backward compatibility class providing the original CommonGuards interface.
  
  This class now delegates to the focused guard modules while maintaining
  the same API that existing code expects.
  """
  
  # Re-export utility function
  extract_param = staticmethod(extract_param)
  
  # Basic guards
  not_none = staticmethod(not_none)
  not_empty = staticmethod(not_empty)
  type_check = staticmethod(type_check)
  
  # Numeric guards  
  positive = staticmethod(positive)
  negative = staticmethod(negative)
  in_range = staticmethod(in_range)
  
  # String guards
  length = staticmethod(length)
  matches_pattern = staticmethod(matches_pattern)
  
  # Specialized validators
  valid_email = staticmethod(valid_email)
  valid_url = staticmethod(valid_url)
  valid_uuid = staticmethod(valid_uuid)
  valid_file_path = staticmethod(valid_file_path)
  
  # Enum guard
  valid_enum = staticmethod(valid_enum)
  
  # Combinators
  all_of = staticmethod(all_of)
  any_of = staticmethod(any_of)
  custom = staticmethod(custom)


# For direct import compatibility
guards = CommonGuards()

# Export all functions for direct import
__all__ = [
  'CommonGuards',
  'guards',
  'extract_param',
  'not_none',
  'not_empty', 
  'type_check',
  'positive',
  'negative',
  'in_range',
  'length',
  'matches_pattern', 
  'valid_email',
  'valid_url',
  'valid_uuid',
  'valid_file_path',
  'valid_enum',
  'all_of',
  'any_of',
  'custom',
]