"""Informational message templates model."""


class InfoMessagesModel:
  """Common informational message templates."""

  # Version control messages
  TAG_CREATED = 'Created tag {tag} on HEAD'
  VERSION_UPDATED = 'Updated pyproject.toml version to {version}'
  COMMIT_CREATED = 'Changes committed successfully!'

  # Build messages
  BUILD_SUCCESS = 'Build completed successfully'
  TESTS_PASSED = 'All tests passed'
  LINTING_COMPLETE = 'Linting completed successfully'
