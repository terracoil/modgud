"""
DrawIOManager v2 - Creates draw.io files using polygon shapes.

This simplified version creates draw.io files that work with standard
polygon shapes rather than complex stencils.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from ..domain.ports.vector_port import VectorPort


class DrawIOManager:
  """Manages conversion of vector sequences to draw.io diagram files."""

  def __init__(self, default_width: float = 800, default_height: float = 600):
    """Initialize with default canvas dimensions."""
    self.default_width = default_width
    self.default_height = default_height

  def vectors_to_drawio(
    self, vectors: Sequence[VectorPort], metadata: dict[str, Any] | None = None
  ) -> str:
    """
    Convert vectors to draw.io XML format.

    Creates a draw.io file with the shape as a polygon using point coordinates.
    """
    if metadata is None:
      metadata = {}

    # Calculate bounding box
    bbox = self._calculate_bounding_box(vectors)

    # Create the draw.io XML structure
    xml_lines = [
      '<mxfile host="app.diagrams.net" agent="modgud/1.0" version="24.8.6">',
      f'  <diagram name="{metadata.get("name", "Shape")}" id="{uuid.uuid4()}">',
      '    <mxGraphModel dx="1242" dy="788" grid="1" gridSize="10" guides="1" '
      'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
      f'pageWidth="{self.default_width}" pageHeight="{self.default_height}" math="0" shadow="0">',
      '      <root>',
      '        <mxCell id="0"/>',
      '        <mxCell id="1" parent="0"/>',
    ]

    # Add the shape as a polygon
    shape_id = str(uuid.uuid4())
    points_str = self._create_points_string(vectors, bbox)

    style = self._generate_polygon_style(metadata)

    xml_lines.extend(
      [
        f'        <mxCell id="{shape_id}" name="" style="{style}" vertex="1" parent="1">',
        f'          <mxGeometry x="100" y="100" width="{bbox["width"]}" '
        f'height="{bbox["height"]}" as="geometry">',
        '            <Array as="points">',
      ]
    )

    # Add each point
    for v in vectors:
      # Transform coordinates relative to bounding box
      rel_x = v.x - bbox['x']
      rel_y = v.y - bbox['y']
      xml_lines.append(f'              <mxPoint x="{100 + rel_x}" y="{100 + rel_y}"/>')

    xml_lines.extend(
      [
        '            </Array>',
        '          </mxGeometry>',
        '        </mxCell>',
        '      </root>',
        '    </mxGraphModel>',
        '  </diagram>',
        '</mxfile>',
      ]
    )

    return '\n'.join(xml_lines)

  def _calculate_bounding_box(self, vectors: Sequence[VectorPort]) -> dict[str, float]:
    """Calculate bounding box for vectors."""
    if not vectors:
      return {'x': 0, 'y': 0, 'width': 100, 'height': 100}

    min_x = min(v.x for v in vectors)
    max_x = max(v.x for v in vectors)
    min_y = min(v.y for v in vectors)
    max_y = max(v.y for v in vectors)

    # Add small padding
    padding = 10

    return {
      'x': min_x - padding,
      'y': min_y - padding,
      'width': max_x - min_x + 2 * padding,
      'height': max_y - min_y + 2 * padding,
    }

  def _create_points_string(self, vectors: Sequence[VectorPort], bbox: dict[str, float]) -> str:
    """Create points string for polygon shape."""
    points = []
    for v in vectors:
      # Normalize to 0-1 range within bounding box
      norm_x = (v.x - bbox['x']) / bbox['width']
      norm_y = (v.y - bbox['y']) / bbox['height']
      points.append(f'{norm_x:.3f} {norm_y:.3f}')

    return ' '.join(points)

  def _generate_polygon_style(self, metadata: dict[str, Any]) -> str:
    """Generate style string for polygon shape."""
    # Default style dictionary
    default_styles = {
      'shape': 'mxgraph.basic.polygon',
      'polyline': '0',
      'fillColor': '#dae8fc',
      'strokeColor': '#6c8ebf',
      'strokeWidth': '2',
      'shadow': '1',
      'rounded': '0',
      'sketch': '1',
      'curveFitting': '1',
      'jiggle': '1',
      'gradientColor': '#7ea6e0',
      'gradientDirection': 'west',
    }

    # Apply custom styles from metadata
    if 'style' in metadata:
      custom_style = metadata['style']
      if isinstance(custom_style, dict):
        default_styles.update(custom_style)

    # Build style string
    style_parts = []
    for key, value in default_styles.items():
      style_parts.append(f'{key}={value}')

    # Add polyCoords if vectors provided
    if 'vectors' in metadata:
      coords = self._create_poly_coords(metadata)
      if coords:
        style_parts.append(f'polyCoords={coords}')

    return ';'.join(style_parts)

  def _create_poly_coords(self, metadata: dict[str, Any]) -> str:
    """Create polyCoords attribute name if vectors provided in metadata."""
    if 'vectors' not in metadata:
      return ''

    vectors = metadata['vectors']
    if not vectors:
      return ''

    # Normalize vectors to 0-1 range
    bbox = self._calculate_bounding_box(vectors)
    coords = []

    for v in vectors:
      norm_x = (v.x - bbox['x']) / bbox['width'] if bbox['width'] > 0 else 0.5
      norm_y = (v.y - bbox['y']) / bbox['height'] if bbox['height'] > 0 else 0.5
      coords.extend([str(norm_x), str(norm_y)])

    return ','.join(coords)

  def create_drawio_file(
    self,
    vectors: Sequence[VectorPort],
    filepath: Path | str,
    metadata: dict[str, Any] | None = None,
  ) -> Path:
    """Create a draw.io file from vectors."""
    filepath = Path(filepath)

    # Ensure .drawio extension
    if filepath.suffix != '.drawio':
      filepath = filepath.with_suffix('.drawio')

    # Add vectors to metadata for polyCoords
    if metadata is None:
      metadata = {}
    metadata['vectors'] = vectors

    # Generate content
    content = self.vectors_to_drawio(vectors, metadata)

    # Write file
    filepath.write_text(content, encoding='utf-8')

    return filepath

  def generate_filename(self, shape_type: str, params: dict[str, Any]) -> str:
    """Generate smart filename with parameters and timestamp."""
    parts = [shape_type]

    # Add key parameters
    for key, value in sorted(params.items())[:3]:
      clean_key = key.replace('_', '').replace('-', '').replace('teeth_', '').replace('torn_', '')

      if isinstance(value, float):
        formatted_value = f'{value:.2f}'.rstrip('0').rstrip('.')
      elif isinstance(value, bool):
        formatted_value = 'y' if value else 'n'
      else:
        formatted_value = str(value)[:10]  # Limit length

      if clean_key and formatted_value:
        parts.append(f'{clean_key}{formatted_value}')

    # Add timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    parts.append(timestamp)

    return '_'.join(parts)
