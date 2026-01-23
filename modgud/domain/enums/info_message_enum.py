"""Domain info message templates for modgud.

Centralized informational message templates following domain-driven design
principles. The domain layer is passive and contains no business logic
- only message template definitions.
"""

from enum import StrEnum

__all__ = ['InfoMessageEnum']


class InfoMessageEnum(StrEnum):
  """Common informational message templates."""

  # Version control messages
  TAG_CREATED = 'Created tag {tag} on HEAD'
  VERSION_UPDATED = 'Updated pyproject.toml version to {version}'
  COMMIT_CREATED = 'Changes committed successfully!'

  # Build messages
  BUILD_SUCCESS = 'Build completed successfully'
  TESTS_PASSED = 'All tests passed'
  LINTING_COMPLETE = 'Linting completed successfully'
