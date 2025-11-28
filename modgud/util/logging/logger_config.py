"""Configuration for Freyja's internal logging."""

import logging
from typing import Optional

from freyja.utils.version import get_freyja_version


class LoggerConfig:
  """Configuration for Freyja's internal logging."""

  version = get_freyja_version()

  def __init__(
    self,
    level: int = logging.INFO,
    format: str = f'[Freyja version: {version}]%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handler: Optional[logging.Handler] = None,
    propagate: bool = True,
    version: str = 'v0.0.0',
  ):
    """Initialize logger configuration."""
    self.level = level
    self.format = format
    self.handler = handler
    self.propagate = propagate
    self.version = version
