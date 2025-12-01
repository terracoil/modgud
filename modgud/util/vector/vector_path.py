"""Vector Path."""

from __future__ import annotations

import copy
from itertools import accumulate
from typing import Generator

from modgud.util.math_util import MathUtil

from .vector import Vector
from .vector_protocol import VectorProtocol


class VectorPath:
  """Vector Path."""

  PATH_HDR_STR: str = '<path>'
  PATH_FTR_STR: str = '</path>'
  PATH_HDR_NAME: str = '<path name="{0}">'
  COMMENT_STR: str = '<!-- {0} -->'
  COMMAND_STR: str = '<{verb} x="{x}" y="{y}" />'
  CLOSE_STR: str = '<close/>'

  VECTORS_FMT: str = '{idx:03d}: {name:<15}: {rel_vec} -> {abs_vec}'

  def __init__(self, home: VectorProtocol = None, close: bool = True, name: str | None = None):
    """Initialize Vector Path."""
    self.origin: VectorProtocol = home if home else Vector.identity()
    self.rel_segments: list[VectorProtocol] = []
    self.abs_segments: list[VectorProtocol] = []
    self.close: bool = close
    self.name: str = name or ''

  def lerp_all(
    self, offset: VectorProtocol = Vector(0, 0), scale: VectorProtocol = Vector(100, 100)
  ):  # noqa: D102
    self.sync_abs_segments()

    # Local import to avoid circular dependency
    from modgud.util.lerper import Lerper

    x_min, x_max = MathUtil.minmax(*[v.x for v in self.abs_segments])
    print(f'foo2, min={x_min}, max={x_max},')
    y_min, y_max = MathUtil.minmax(*[v.y for v in self.abs_segments])
    print(f'foo3, min={y_min}, max={y_max},')
    start = Vector(x_min, y_min)
    stop = Vector(x_max, y_max)
    from_lerper: Lerper[VectorProtocol] = Lerper[VectorProtocol](start=start, stop=stop)
    to_lerper: Lerper[VectorProtocol] = Lerper[VectorProtocol](start=offset, stop=scale)

    def translate(v: VectorProtocol) -> VectorProtocol:
      return to_lerper.lerp(from_lerper.rlerp(v))

    self.abs_segments = [translate(v) for v in self.abs_segments]

  def absolute_segments(self, sync: bool = False) -> list[VectorProtocol]:
    """Return absolute segments; syncing if specified."""
    if sync:
      self.sync_abs_segments()

    return self.abs_segments

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

  def clone(self, name=None, origin: VectorProtocol | None = None) -> VectorPath:
    """Clone Vector Path."""
    new_path: VectorPath = copy.deepcopy(self)
    new_path.name = name or (f'Copy of {self.name}' if self.name else None)
    new_path.origin = origin or self.origin
    return new_path

  def relative_segments(self) -> list[VectorProtocol]:
    """Return relative segments, including origin."""
    return [self.origin] + self.rel_segments

  def sync_abs_segments(self):
    """Sync absolute segments with relative segments."""
    rsegs: list[VectorProtocol] = self.relative_segments()
    print(f'Syncing {len(rsegs)} relative segments to absolute segments')
    self.abs_segments = list(accumulate(rsegs))

  def __str__(self) -> str:
    """Return string representation of path."""
    rel_seg_strs = [v.format() for v in self.relative_segments()]
    return '\n'.join(rel_seg_strs)

  def quad_path(self, sync: bool = False) -> Generator[str, None, None]:
    """Return quad path string."""

  def svg_path(self, sync: bool = False) -> Generator[str]:
    """Generate SVG path string."""
    # Header:
    yield self.PATH_HDR_NAME.format(self.name) if self.name else self.PATH_HDR_STR

    # Walk through path and output appropriate commands
    for i, vec in enumerate(self.absolute_segments(sync)):
      verb: str = 'move' if i == 0 else 'line'
      if vec.name:
        yield f'  {self.COMMENT_STR.format(vec.name)}'
      yield f'  {self.COMMAND_STR.format(verb=verb, x=round(vec.x, 4), y=round(vec.y, 4))}'

    yield f'  {self.CLOSE_STR}'
    yield self.PATH_FTR_STR

  def __len__(self) -> int:
    """Return number of segments."""
    return max(len(self.rel_segments) + 1, len(self.abs_segments))
