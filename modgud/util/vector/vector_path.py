"""Vector Path."""

from __future__ import annotations

import copy
import operator
import textwrap
from enum import IntEnum, StrEnum, auto
from typing import Callable, Generator, Iterable, Sequence

from modgud.util.lerper import Lerper

from .vector import Vector
from .vector_protocol import VectorProtocol


class VectorPath:
  """
  Represents a sequence of connected line segments for geometric path operations.

  Enables SVG path generation, geometric transformations, and smooth interpolation
  between path states. Maintains both relative (displacement) and absolute (position)
  representations for flexible path manipulation in graphics and CAD applications.
  """

  class PathVerbEnum(StrEnum):
    """Enumeration of SVG path commands."""

    none = auto()
    move = auto()
    line = auto()
    rline = auto()
    quad = auto()

  class PathStrategy(IntEnum):
    """Enumeration of path generation strategies."""

    absolute = auto()
    relative = auto()

  TAB = '  '
  PATH_HDR_STR: str = '<path>'
  PATH_FTR_STR: str = '</path>'
  PATH_HDR_NAME: str = '<path name="{0}">'
  COMMENT_STR: str = '<!-- {0} -->'
  COMMAND_STR: str = '<{verb} x="{x}" y="{y}" />'
  QUAD_CMD: str = '<quad x2="{x2}" y2="{y2}" x1="{x1}" y1="{y1}" />'
  CLOSE_STR: str = '<close/>'

  VECTORS_FMT: str = '{idx:03d}: {name:<15}: {rel_vec} -> {abs_vec}'
  VECTOR_RMT: str = '{name:<20}{vec}'

  SegmentType = VectorProtocol | Sequence[VectorProtocol]

  def __init__(
    self,
    close: bool = True,
    name: str = '',
    abs_segments: SegmentType | None = None,
    rel_segments: SegmentType | None = None,
  ):
    """
    Initialize path with starting position and configuration.

    :param close: Whether path should close back to origin for shapes
    :param name: Optional identifier for debugging and SVG generation
    """
    if abs_segments and rel_segments:
      raise ValueError('Cannot specify both absolute and relative segments')

    self._index: int = 0
    self.close: bool = close

    if rel_segments:
      self.rel_segments = rel_segments if isinstance(rel_segments, Sequence) else [rel_segments]
    else:
      self.rel_segments = [Vector.ZERO]

    if abs_segments:
      self.rel_segments.extend(self.gen_relative_segments(abs_segments))

    self.name: str = name

  @property
  def origin(self) -> VectorProtocol:
    return self.rel_segments[0] if self.rel_segments else Vector.ZERO

  @origin.setter
  def origin(self, value: VectorProtocol) -> None:
    self.rel_segments.pop(0)
    self.push_segment(value, 0)

  @property
  def relative_segments(self) -> list[VectorProtocol]:
    """
    Get complete segment list starting with origin.

    Provides unified access to all path components for iteration and analysis.
    First element is origin position, subsequent elements are displacement vectors.
    """
    return self.rel_segments

  def gen_absolute_segments(self) -> Generator[VectorProtocol]:
    """
    Generate absolute coordinate positions from relative segments.

    Accumulates displacement vectors to produce actual coordinate positions.
    Essential for rendering paths in graphics systems that need absolute positioning.
    """
    prev: VectorProtocol = Vector.ZERO
    for seg in self.rel_segments:
      # Accumulate displacement to get absolute position
      prev = prev + seg
      yield prev

  def gen_relative_segments(
    self, abs_segments: Iterable[VectorProtocol]
  ) -> Generator[VectorProtocol]:
    """
    Convert absolute positions back to relative displacement vectors.

    Used when transforming a path - convert to absolute, transform, then back to relative.
    Maintains the relative segment representation for consistent path operations.
    """
    prev: VectorProtocol = Vector.ZERO
    for seg in abs_segments:
      # Subtract previous position to get displacement
      yield prev.inverse() + seg
      prev = seg

  def lerp_all(self, stop: VectorProtocol, offset: VectorProtocol = Vector.ZERO) -> VectorPath:
    """
    Apply scaling transformation to entire path using enhanced Lerper functionality.

    Scales path coordinates by stop vector and adds offset.
    Essential for resizing paths, positioning within layouts, or converting
    between coordinate systems.
    """
    # Create transformer using enhanced Lerper
    transformer = Lerper.from_transform(scale=stop, offset=offset)
    
    # Transform all absolute positions using the Lerper's scale method
    abs_segments = [transformer.scale(v, stop, offset) for v in self.gen_absolute_segments()]
    
    # Convert back to relative segments
    self.rel_segments = (
      list(self.gen_relative_segments(abs_segments))[1:] if len(abs_segments) > 1 else []
    )
    return self

  def push_segment(self, segments: SegmentType, index: int = -1) -> None:
    """
    Add segment(s) to extend the path.

    Accepts single vectors or lists for efficient batch operations.
    Relative segments represent movement from current position rather
    than absolute coordinates, enabling flexible path composition.
    """
    if isinstance(segments, Iterable):
      if index == -1 or index >= len(self.rel_segments):
        # Extend list with list of segments:
        self.rel_segments.extend(segments)
      else:
        # Insert segments
        for s in reversed(segments):
          self.rel_segments.insert(index, s)
        self.rel_segments.insert(index, *segments)
    else:
      self.rel_segments.append(segments)

  def clone(self, name: str | None = None, origin: VectorProtocol | None = None) -> VectorPath:
    """
    Create independent copy with optional modifications.

    Enables path variations and templates - clone a base path then modify
    specific aspects without affecting the original. Essential for creating
    multiple similar paths with different origins or transformations.
    """
    new_path: VectorPath = copy.deepcopy(self)
    new_path.name = name or (f'Copy of {self.name}' if self.name else None)
    new_path.origin = origin or self.origin
    return new_path

  def reverse(self) -> VectorPath:
    """Reverse path segments in place."""
    abs_segments = reversed(list(self.gen_absolute_segments()))
    self.rel_segments = list(self.gen_relative_segments(abs_segments))
    return self

  @staticmethod
  def _format_float(f: float, precision: int = 2) -> float:
    m: float = float(10**precision)
    r: float = round(f * m, 0)
    return r / m

  def quad_path(self) -> Generator[str, None, None]:
    """
    Generate quadrilateral path markup (placeholder implementation).

    Reserved for future quad-specific path generation. Currently not implemented
    as SVG path generation covers most use cases for vector graphics output.
    """
    f: Callable = self._format_float

    def format_quad(v: VectorProtocol, cp: VectorProtocol) -> str:
      print(f'Creating quad from {v} with {cp}')
      cmd: str = self.QUAD_CMD.format(x2=f(v.x), y2=f(v.y), x1=f(cp.x), y1=f(cp.y))
      print(f'Created cmd: {cmd}')
      return textwrap.indent(cmd, self.TAB)

    # Generate opening tag with optional name attribute
    yield self.PATH_HDR_NAME.format(f'{self.name}-quad') if self.name else self.PATH_HDR_STR
    yield textwrap.indent(
      self.COMMAND_STR.format(verb='move', x=f(self.origin.x), y=f(self.origin.y)), self.TAB
    )

    # Convert each absolute position to SVG command
    segments: list[VectorProtocol] = list(self.gen_absolute_segments())

    for i in range(1, len(segments) - 1, 2):
      print('Segments ', i, len(segments))
      if segments[i].name:
        yield textwrap.indent(self.COMMENT_STR.format(segments[i].name), self.TAB)
      yield format_quad(segments[i], segments[i + 1])

    # Close path if configured for shapes
    if self.close:
      yield f'  {self.CLOSE_STR}'
    yield self.PATH_FTR_STR

  @classmethod
  def get_svg_verb(
    cls, seg_idx: int, absolute: bool = False, custom: PathVerbEnum = PathVerbEnum.none
  ) -> PathVerbEnum:
    if seg_idx == 0:
      verb = cls.PathVerbEnum.move
    elif custom != cls.PathVerbEnum.none:
      verb = custom
    else:
      verb = cls.PathVerbEnum.line if absolute else cls.PathVerbEnum.rline

    return verb

  def svg_path(self, absolute: bool = True) -> Generator[str, None, None]:
    """
    Generate SVG path markup from vector segments.

    Converts path to standard SVG format with move/line commands.
    Essential for rendering vector paths in web graphics and CAD exports.
    Includes optional naming and comments for debugging complex paths.
    """
    # Generate opening tag with optional name attribute
    yield self.PATH_HDR_NAME.format(self.name) if self.name else self.PATH_HDR_STR
    f: Callable = self._format_float

    # Convert each absolute position to SVG command
    segments: Iterable[VectorProtocol] = (
      self.gen_absolute_segments() if absolute else self.relative_segments
    )

    for i, vec in enumerate(segments):
      verb: str = str(self.get_svg_verb(i, absolute))
      if vec.name:
        yield textwrap.indent(self.COMMENT_STR.format(vec.name), self.TAB)
      yield textwrap.indent(self.COMMAND_STR.format(verb=verb, x=f(vec.x), y=f(vec.y)), self.TAB)

    # Close path if configured for shapes
    if self.close:
      yield textwrap.indent(self.CLOSE_STR, self.TAB)
    yield self.PATH_FTR_STR

  def _transform(self, other: VectorProtocol, op: Callable) -> VectorPath:
    """Transform using given a VectorProtocol and operation. Preserves other.name per convention."""
    vp = VectorPath(rel_segments=op(self.origin, other), name=self.name)
    vp.push_segment([op(v, other) for v in self.rel_segments])
    return vp

  def __add__(self, other: VectorProtocol) -> VectorPath:
    """Add vector to all vectors in path."""
    return self._transform(other, operator.add)

  def __div__(self, other: VectorProtocol) -> VectorPath:
    """Multiply all vectors in path by given vector."""
    return self._transform(other, operator.mul)

  def __iter__(self):
    # This method should return an iterator object.
    # In this case, the instance of MyIterableClass itself acts as the iterator.
    self._index = 0  # Reset index for new iteration
    return self

  def __next__(self):
    if self._index < len(self):
      item = self[self._index]
      self._index += 1
      return item
    else:
      raise StopIteration

  def __sub__(self, other: VectorProtocol) -> VectorPath:
    """Add vector to all vectors in path."""
    return self._transform(other, operator.truediv)

  def __mul__(self, other: VectorProtocol) -> VectorPath:
    """Multiply all vectors in path by given vector."""
    return self._transform(other, operator.mul)

  def __len__(self) -> int:
    """
    Return total number of path points including origin (at index 0)

    Counts origin plus all relative segments for total path complexity.
    Used for path comparison, memory estimation, and iteration bounds.
    """
    return len(self.rel_segments)

  def __getitem__(self, key: int | slice) -> VectorProtocol | list[VectorProtocol]:
    """
    Access path points by index.

    Index 0 returns the origin point. Index n (where n >= 1) returns
    the nth relative segment (rel_segments[n-1]).

    :param key: Zero-based index into path points
    :return: VectorProtocol at the specified index
    :raises IndexError: If index is out of bounds
    """
    total_length = len(self.rel_segments)
    
    if isinstance(key, slice):
      result: list[VectorProtocol] = self.rel_segments[key]
    elif isinstance(key, int):
      if key < 0 or key >= total_length:
        raise IndexError(f'Path index {key} out of range [0, {total_length - 1}]')
      result: VectorProtocol = self.rel_segments[key]
    else:
      raise TypeError(f'Invalid key type for VectorPath[key] -> key: {type(key)}={key}')

    return result

  def __setitem__(self, key: int, value: VectorProtocol) -> None:
    """
    Set path point at specified index.

    Allows assignment to path points using bracket notation. Index 0 sets
    the origin point, subsequent indices set relative segments.

    :param key: Zero-based index into path points
    :param value: VectorProtocol to assign at the specified index
    :raises IndexError: If index is out of bounds
    :raises TypeError: If value is not a VectorProtocol
    """
    total_length = len(self.rel_segments)
    if key < 0 or key >= total_length:
      raise IndexError(f'Path index {key} out of range [0, {total_length - 1}]')

    # Type check to ensure value is a VectorProtocol
    if not hasattr(value, 'x') or not hasattr(value, 'y'):
      raise TypeError(f'Value must be a VectorProtocol, got {type(value)}')

    self.rel_segments[key] = value

  def __str__(self) -> str:
    """
    Format path as human-readable coordinate list.

    Shows origin and all displacement vectors for debugging and inspection.
    Each vector displays on separate line with consistent formatting.
    """
    # for i, v in enumerate(self.gen_absolute_segments()):
    #   print(f"{i} {v}")
    rel_seg_strs = [f'{v.name:<40}{v.format(name=False)}' for v in self.gen_absolute_segments()]
    return '\n'.join(rel_seg_strs)
