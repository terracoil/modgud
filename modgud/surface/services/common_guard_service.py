"""
Common guard validators - now delegating to modular implementations.

This module maintains backward compatibility by re-exporting the CommonGuards
class while the actual implementation has been decomposed into focused modules
for better maintainability and single responsibility.
"""

# Import from the new modular structure
from .guards import CommonGuards, guards, extract_param

# Re-export for backward compatibility
__all__ = ['CommonGuards', 'guards', 'extract_param']