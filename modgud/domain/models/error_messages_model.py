"""Error message templates model."""


class ErrorMessagesModel:
  """Common error message templates used throughout the library."""

  # Parameter validation messages
  PARAM_REQUIRED = '{param_name} is required'
  PARAM_MUST_BE_POSITIVE = '{param_name} must be positive'
  PARAM_MUST_BE_IN_RANGE = '{param_name} must be between {min_val} and {max_val}'
  PARAM_MUST_BE_TYPE = '{param_name} must be of type {expected_type}'
  PARAM_MUST_MATCH_PATTERN = '{param_name} must match pattern {pattern}'

  # File validation messages
  PATH_MUST_EXIST = '{param_name} does not exist: {value}'
  PATH_MUST_BE_FILE = '{param_name} must be a file: {value}'
  PATH_MUST_BE_DIR = '{param_name} must be a directory: {value}'

  # URL validation messages
  URL_MUST_HAVE_SCHEME = '{param_name} must include a scheme (http/https): {value}'
  URL_NOT_VALID = '{param_name} is not a valid URL: {value}'

  # Enum validation messages
  ENUM_INVALID_VALUE = '{param_name} must be one of {valid_values}: got {value}'
  ENUM_INVALID_TYPE = '{param_name} must be a valid {enum_class} value'

  # Registry messages
  GUARD_ALREADY_REGISTERED_GLOBAL = "Guard '{name}' is already registered in global namespace"
  GUARD_ALREADY_REGISTERED_NS = "Guard '{name}' is already registered in namespace '{namespace}'"

  # Generic guard messages
  GUARD_FAILED_GENERIC = 'Guard clause failed'
  VALUE_NOT_EMPTY = '{param_name} cannot be empty'
  VALUE_NOT_NONE = '{param_name} cannot be None'
