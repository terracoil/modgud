"""String utility functions for case conversion and naming helpers."""

import re


class StrUtils:
  """Utility class for string operations."""

  @classmethod
  def to_camel_case(cls, snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

  @classmethod
  def to_pascal_case(cls, snake_str: str) -> str:
    """Convert snake_case to PascalCase."""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

  @classmethod
  def to_snake_case(cls, camel_str: str) -> str:
    """Convert camelCase or PascalCase to snake_case."""
    # Insert an underscore before any uppercase letter preceded by a lowercase letter
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    # Insert an underscore before any uppercase letter preceded by a lowercase letter or number
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

  @classmethod
  def to_kebab_case(cls, input_str: str) -> str:
    """Convert any case to kebab-case."""
    # First convert to snake_case, then replace underscores with hyphens
    snake = cls.to_snake_case(input_str) if '_' not in input_str else input_str
    return snake.replace('_', '-')

  @classmethod
  def to_constant_case(cls, input_str: str) -> str:
    """Convert any case to CONSTANT_CASE."""
    # First convert to snake_case, then uppercase
    snake = cls.to_snake_case(input_str) if '_' not in input_str else input_str
    return snake.upper()

  @classmethod
  def pluralize(cls, word: str) -> str:
    """Pluralize a word using simple rules for common cases."""
    if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
      return word[:-1] + 'ies'
    elif word.endswith(('s', 'ss', 'sh', 'ch', 'x', 'z')):
      return word + 'es'
    elif word.endswith('fe'):
      return word[:-2] + 'ves'
    elif word.endswith('f'):
      return word[:-1] + 'ves'
    else:
      return word + 's'

  @classmethod
  def singularize(cls, word: str) -> str:
    """Singularize a word using simple rules for common cases."""
    if word.endswith('ies') and len(word) > 3:
      return word[:-3] + 'y'
    elif word.endswith('es') and len(word) > 2:
      # Check if it's a special case
      if word.endswith(('sses', 'shes', 'ches', 'xes', 'zes')):
        return word[:-2]
      return word[:-2]
    elif word.endswith('ves'):
      if len(word) > 3 and word[-4] not in 'aeiou':
        return word[:-3] + 'f'
      return word[:-3] + 'fe'
    elif word.endswith('s') and not word.endswith('ss'):
      return word[:-1]
    else:
      return word

  @classmethod
  def is_valid_identifier(cls, name: str) -> bool:
    """Check if string is a valid identifier (variable/class name)."""
    return bool(name and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))

  @classmethod
  def sanitize_identifier(cls, name: str) -> str:
    """Sanitize string to be a valid identifier."""
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Ensure it starts with a letter or underscore
    if sanitized and sanitized[0].isdigit():
      sanitized = '_' + sanitized
    return sanitized if sanitized else 'identifier'

  @classmethod
  def truncate(cls, text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
      return text
    return text[: max_length - len(suffix)] + suffix

  @classmethod
  def remove_prefix(cls, text: str, prefix: str) -> str:
    """Remove prefix from string if present."""
    if text.startswith(prefix):
      return text[len(prefix) :]
    return text

  @classmethod
  def remove_suffix(cls, text: str, suffix: str) -> str:
    """Remove suffix from string if present."""
    if text.endswith(suffix):
      return text[: -len(suffix)]
    return text

  @classmethod
  def to_pct_str(cls, n: float, p: int = 1, pad: int = 0) -> str:
    """Return a percentage string.

    :param n: Percentage value where (0.0 <= n <= 1.0)
    :param p: Precision - number of decimal points
    :param pad: Additional padding to add to minimum length
    """
    pct_str = f'{n * 100:.{p}f}%'
    if pad:
      min_len = 4 + (p + 1 if p else 0)
      pct_str = f'{pct_str:>{min_len + pad}}'
    return pct_str
