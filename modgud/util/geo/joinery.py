"""Joinery calculations for woodworking joints like dovetails and notches."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from modgud.domain.ports.vector_port import VectorPort
from modgud.util.math_util import MathUtil

from .vector import Vector
from .vector_path import VectorPath


@dataclass(frozen=True)
class Joinery:
  """Calculate coordinates for woodworking joints including dovetails, notches, and slanted joints."""

  slope_pct: float = 0.1
  teeth_cnt: int = 2
  tooth_depth_pct: float = 0.35
  corner_pct: float = 0.1

  def __post_init__(self):
    """Validate parameters after initialization."""
    self._validate_parameters()

  def build_shape(self) -> Sequence[VectorPort]:
    """Build the primary teeth shape for the joint.

    Returns the main teeth component as a sequence of vectors.
    Use build_adapter_shape() and build_port_shape() for other components.

    :returns: Sequence of VectorPort objects representing the teeth
    """
    teeth_path = self._create_teeth_path_internal()

    # Scale to final dimensions and return absolute positions
    teeth_path.transform_all(Vector(100, 100))
    return list(teeth_path.gen_absolute_segments())

  def build_adapter_shape(self) -> Sequence[VectorPort]:
    """Build the adapter (left) enclosure shape.

    :returns: Sequence of VectorPort objects representing the adapter
    """
    teeth_path = self._create_teeth_path_internal()
    adapter_path = self._create_adapter_path(
      teeth_path, self._get_joint_type_name(), self.tooth_depth_pct, self.corner_pct
    )
    return list(adapter_path.gen_absolute_segments())

  def build_port_shape(self) -> Sequence[VectorPort]:
    """Build the port (right) enclosure shape.

    :returns: Sequence of VectorPort objects representing the port
    """
    teeth_path = self._create_teeth_path_internal()
    notches_path = self._create_notches_path(teeth_path, self._get_joint_type_name())
    port_path = self._create_port_path(
      notches_path, self._get_joint_type_name(), self.tooth_depth_pct, self.corner_pct
    )
    return list(port_path.gen_absolute_segments())

  def _validate_parameters(self) -> None:
    """Validate all input parameters."""
    # Validate slope_pct
    if self.slope_pct < -0.7 or self.slope_pct > 0.3:
      raise ValueError('slope_pct should be between -70% and 30%')

    # Validate tooth_depth_pct
    if self.tooth_depth_pct < 0.1 or self.tooth_depth_pct > 0.9:
      raise ValueError('tooth_depth_pct should be between 10% and 90%')

    # Validate teeth_cnt
    if self.teeth_cnt < 1 or self.teeth_cnt > 10:
      raise ValueError('teeth_cnt should be between 1 and 10')

    # Validate corner_pct
    if self.corner_pct < 0.0 or self.corner_pct > 0.5:
      raise ValueError('corner_pct should be between 0% and 50%')

  def _get_joint_type_name(self) -> str:
    """Get the joint type name based on slope."""
    name = 'notched'
    if not MathUtil.is_zero(self.slope_pct):
      name = 'dovetail' if self.slope_pct > 0.0 else 'slanted'
    return name

  def _create_teeth_path_internal(self) -> VectorPath:
    """Create the internal teeth path for calculations."""
    # Calculate base dimensions
    base_pct = 1.0 / (self.teeth_cnt * 2.0)
    slant_diff = base_pct * self.slope_pct
    end_width = base_pct + slant_diff
    stub_size = end_width / 2.0

    # Validate slope isn't too extreme
    if slant_diff > (base_pct / 2.0):
      max_slope = slant_diff / base_pct
      raise ValueError(
        f'slope_pct is too great. It should be <= {max_slope:.2f} with the current parameters.'
      )

    # Create teeth path
    name = self._get_joint_type_name()
    path_teeth = self._create_teeth_path(name, self.teeth_cnt, stub_size, slant_diff, end_width)

    return path_teeth

  def _create_teeth_path(
    self, name: str, teeth_cnt: int, stub_size: float, slant_diff: float, end_width: float
  ) -> VectorPath:
    """Create the teeth path for the joint."""
    path_teeth = VectorPath(rel_segments=Vector.ZERO, name=f'{name}Teeth')
    path_teeth.push_segment(Vector(stub_size, 0, name='begStub'))

    # Add teeth segments
    for t in range(teeth_cnt):
      tooth_segments = self._create_tooth_segments(
        slant_diff, end_width, t, gap=(t < teeth_cnt - 1)
      )
      path_teeth.push_segment(tooth_segments)

    path_teeth.push_segment(Vector(stub_size, 0, name='endStub'))
    return path_teeth

  def _create_notches_path(self, path_teeth: VectorPath, name: str) -> VectorPath:
    """Create slots/notches that mate with the teeth."""
    path_notches = path_teeth.clone(name=f'{name}Slots')

    # Rename segments from tooth to slot
    for i in range(len(path_notches)):
      v = path_notches[i]
      if v.name == 'begStub':
        path_notches[i] = v.clone(name='endStub')
      elif v.name == 'endStub':
        path_notches[i] = v.clone(name='begStub')
      elif v.name:
        path_notches[i] = v.clone(name=v.name.replace('tooth', 'slot'))

    path_notches.reverse()
    return path_notches

  def _create_adapter_path(
    self, path_teeth: VectorPath, name: str, tooth_depth_pct: float, corner_pct: float
  ) -> VectorPath:
    """Create the adapter (left) enclosure path."""
    enclosure_pct = 1.0 - tooth_depth_pct
    corner_x = corner_pct
    corner_y = corner_pct * 2

    path_adapter = path_teeth.clone(name=f'{name}Adapter')
    base_name = 'adapterEnclosure'

    # Scale teeth to tooth depth
    path_adapter.transform_all(Vector(1, tooth_depth_pct))
    path_adapter.origin = Vector(0, enclosure_pct)

    # Add enclosure segments
    path_adapter.push_segment(Vector(0, -enclosure_pct, name=f'{base_name}Bottom'))
    path_adapter.push_segment(Vector(-(1.0 - corner_x), 0, name=f'{base_name}Left'))
    path_adapter.push_segment(Vector(-corner_x, corner_y, name=f'{base_name}Corner'))

    # Scale to final size
    path_adapter.transform_all(Vector(100, 100))

    return path_adapter

  def _create_port_path(
    self, path_notches: VectorPath, name: str, tooth_depth_pct: float, corner_pct: float
  ) -> VectorPath:
    """Create the port (right) enclosure path."""
    corner_x = corner_pct
    corner_y = corner_pct * 2

    path_port = path_notches.clone(name=f'{name}Port')
    base_name = 'portEnclosure'

    # Scale teeth to tooth depth
    path_port.transform_all(Vector(1, tooth_depth_pct))

    # Add enclosure segments
    path_port.push_segment(Vector(0, 1, name=f'{base_name}Top'))
    path_port.push_segment(Vector(1.0 - corner_x, 0, name=f'{base_name}Right'))
    path_port.push_segment(Vector(corner_x, -corner_y, name=f'{base_name}Corner'))

    # Scale to final size
    path_port.transform_all(Vector(100, 100))

    return path_port

  @staticmethod
  def _create_tooth_segments(
    slant_diff: float, end_width: float, tooth_idx: int, gap: bool
  ) -> list[VectorPort]:
    """Create segments for a single tooth.

    :param slant_diff: Amount of slant for dovetail angle
    :param end_width: Width at the end of the tooth
    :param tooth_idx: Index of this tooth (0-based)
    :param gap: Whether to add a gap segment after this tooth
    :returns: List of Vector segments defining the tooth
    """
    name_base = f'tooth-{tooth_idx + 1}'
    depth_pct = 1.0

    tooth_segments = [
      Vector(-slant_diff, depth_pct, name=f'{name_base}-side-a'),
      Vector(end_width, 0, name=f'{name_base}-end'),
      Vector(-slant_diff, -depth_pct, name=f'{name_base}-side-b'),
    ]

    # Add gap if specified
    if gap:
      tooth_segments.append(Vector(end_width, 0, name=f'{name_base}-gap'))

    return tooth_segments
