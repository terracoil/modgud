"""Vector Path."""

from __future__ import annotations

import copy
from itertools import accumulate
from typing import Generator

from .types import VectorProtocol
from .vector import Vector


class VectorPath:
  """Vector Path."""

  PATH_HDR_STR: str = '<path>'
  PATH_FTR_STR: str = '</path>'
  PATH_HDR_NAME: str = '<path name="{0}">'
  COMMENT_STR: str = '<!-- {0} -->'
  COMMAND_STR: str = '<{verb} x="{x}" y="{y}" />'
  CLOSE_STR: str = '<close/>'

  def __init__(self, start: VectorProtocol = None, close: bool = True, name: str | None = None):
    """Initialize Vector Path."""
    self.home: VectorProtocol = start if start else Vector.ZERO
    self.rel_segments: list[VectorProtocol] = [self.home]
    self.abs_segments: list[VectorProtocol] = [self.home]
    self.close: bool = close
    self.name: str = name or ''

  def clone(self, name=None) -> VectorPath:
    """Clone Vector Path."""
    new_path: VectorPath = copy.deepcopy(self)
    new_path.name = name or (f'Copy of {self.name}' if self.name else None)
    return new_path

  @property
  def absolute_segments(self, sync_relative: bool = False):
    """Return absolute segments."""
    if sync_relative:
      self.sync_abs_segments()

    return self.abs_segments

  @property
  def relative_segments(self):
    """Return relative segments."""
    return self.rel_segments

  def add_relative_segment(self, segments: VectorProtocol | list[VectorProtocol]):
    """Add relative segment(s) to path."""
    if isinstance(segments, list):
      self.rel_segments.extend(segments)
    else:
      self.rel_segments.append(segments)

  def add_absolute_segment(self, segments: VectorProtocol | list[VectorProtocol]):
    """Add absolute segment(s) to path."""
    if isinstance(segments, list):
      self.abs_segments.extend(segments)
    else:
      self.abs_segments.append(segments)

  def sync_abs_segments(self):
    """Sync absolute segments with relative segments."""
    self.abs_segments = list(accumulate(self.rel_segments))

  def _format_vectors_at(self, idx: int) -> str:
    assert len(self.abs_segments) == len(self.rel_segments), (
      f'Should have equal length in segment arrays: {len(self.rel_segments)} <> {len(self.abs_segments)}'
    )
    assert idx < len(self.rel_segments), f'Index out of bounds: {idx} <> {len(self.rel_segments)}'

    abs_vec: VectorProtocol = self.abs_segments[idx]
    rel_vec: VectorProtocol = self.rel_segments[idx]

    vec_fmt: str = '{x:000.2f}'

    name: str = rel_vec.name or ''
    x1: str = vec_fmt.format(x=rel_vec.x)
    y1: str = vec_fmt.format(x=rel_vec.y)
    x2: str = vec_fmt.format(x=abs_vec.x)
    y2: str = vec_fmt.format(x=abs_vec.y)
    return f'{idx:03d}: {name:<15}: [{x1:>7}, {y1:>7}] -> [{x2:>7}, {y2:>7}]'

  def __len__(self) -> int:
    """Return number of segments."""
    return max(len(self.rel_segments), len(self.abs_segments))

  def __str__(self) -> str:
    """Return string representation of path."""
    assert len(self.abs_segments) == len(self.rel_segments)
    vec_strs: list[str] = [self._format_vectors_at(i) for i in range(len(self.rel_segments))]
    return '\n'.join(vec_strs)

  def svg_path(self, sync: bool = False) -> Generator[str]:
    """Generate SVG path string."""
    if sync:
      self.sync_abs_segments()

    # Header:
    yield self.PATH_HDR_NAME.format(self.name) if self.name else self.PATH_HDR_STR

    # Walk through path and output appropriate commands
    for i, vec in enumerate(self.abs_segments):
      verb: str = 'move' if i == 0 else 'line'
      if vec.name:
        yield f'  {self.COMMENT_STR.format(vec.name)}'
      yield f'  {self.COMMAND_STR.format(verb=verb, x=round(vec.x,4), y=round(vec.y,4))}'

    yield f'  {self.CLOSE_STR}'
    yield self.PATH_FTR_STR
