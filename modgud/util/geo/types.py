"""Types, interfaces, etc for geo utils."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HexMetadata:
  """Preserved metadata from hex string parsing for output format consistency."""

  prefix: str = '#'
  short_form: bool = False
  uppercase: bool = False


type SimpleNum = float | int
