"""DrawIOManager - Converts vector sequences to draw.io diagram files.

This module provides functionality to generate draw.io (diagrams.net) files
from vector sequences produced by shape generators. It creates valid mxGraph
XML format files that can be opened and edited in draw.io.
"""

import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from modgud.domain.ports import VectorPort


class DrawIOManager:
  """Manages conversion of vector sequences to draw.io diagram files.

  This class handles:
  - Vector to mxGraph XML conversion
  - Coordinate system transformation
  - Smart file naming with parameters
  - File I/O operations
  """

  def __init__(self, default_width: float = 800, default_height: float = 600):
    """Initialize DrawIOManager with default canvas dimensions.

    :param default_width: Default canvas width in pixels
    :param default_height: Default canvas height in pixels
    """
    self.default_width = default_width
    self.default_height = default_height

  def vectors_to_drawio(
    self, vectors: Sequence[VectorPort], metadata: dict[str, Any] | None = None
  ) -> str:
    """Convert a sequence of vectors to draw.io XML format.

    :param vectors: Sequence of VectorPort objects representing the shape
    :param metadata: Optional metadata including shape name, parameters, etc.
    :returns: XML string in draw.io format
    """
    if metadata is None:
      metadata = {}

    # Create root mxfile element
    root = ET.Element(
      'mxfile',
      {
        'host': 'modgud.shapetool',
        'modified': datetime.now().isoformat(),
        'agent': 'modgud DrawIOManager v1.0',
        'version': '24.8.6',
      },
    )

    # Create diagram
    diagram = ET.SubElement(
      root, 'diagram', {'name': metadata.get('name', 'Shape'), 'id': str(uuid.uuid4())}
    )

    # Create mxGraphModel
    graph_model = ET.SubElement(
      diagram,
      'mxGraphModel',
      {
        'dx': '0',
        'dy': '0',
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': str(self.default_width),
        'pageHeight': str(self.default_height),
        'math': '0',
        'shadow': '0',
      },
    )

    # Create root cells
    root_element = ET.SubElement(graph_model, 'root')
    ET.SubElement(root_element, 'mxCell', {'id': '0'})
    ET.SubElement(root_element, 'mxCell', {'id': '1', 'parent': '0'})

    # Calculate bounding box and normalize vectors
    bbox = self._calculate_bounding_box(vectors)
    normalized_vectors = self._normalize_vectors(vectors, bbox)

    # Create stencil shape string
    stencil_data = self._create_stencil_data(normalized_vectors)

    # Create shape cell with stencil
    shape_cell = ET.SubElement(
      root_element,
      'mxCell',
      {
        'id': '2',
        'name': metadata.get('label', ''),
        'style': self._generate_stencil_style(stencil_data, metadata),
        'parent': '1',
        'vertex': '1',
      },
    )

    # Add geometry
    ET.SubElement(
      shape_cell,
      'mxGeometry',
      {
        'x': str(100),  # Fixed position for now
        'y': str(100),
        'width': str(bbox['width']),
        'height': str(bbox['height']),
        'as': 'geometry',
      },
    )

    # Convert to string with proper formatting
    return self._prettify_xml(root)

  def _normalize_vectors(
    self, vectors: Sequence[VectorPort], bbox: dict[str, float]
  ) -> list[tuple[float, float]]:
    """Normalize vectors to 0-1 range for stencil format.

    :param vectors: Sequence of VectorPort objects
    :param bbox: Bounding box dictionary
    :returns: List of normalized (x, y) tuples
    """
    if not vectors:
      return []

    min_x = bbox['x'] + 20  # Remove padding
    min_y = bbox['y'] + 20
    width = bbox['width'] - 40
    height = bbox['height'] - 40

    normalized = []
    for v in vectors:
      norm_x = (v.x - min_x) / width if width > 0 else 0.5
      norm_y = (v.y - min_y) / height if height > 0 else 0.5
      normalized.append((norm_x, norm_y))

    return normalized

  def _create_stencil_data(self, normalized_vectors: list[tuple[float, float]]) -> str:
    """Create stencil data string from normalized vectors.

    :param normalized_vectors: List of (x, y) tuples in 0-1 range
    :returns: Stencil path data string
    """
    if not normalized_vectors:
      return ''

    # Start with move command
    commands = []
    first_x, first_y = normalized_vectors[0]
    commands.append(f'm {first_x:.4f} {first_y:.4f}')

    # Add line commands for subsequent points
    for i in range(1, len(normalized_vectors)):
      x, y = normalized_vectors[i]
      commands.append(f'l {x:.4f} {y:.4f}')

    # Close path if needed
    if len(normalized_vectors) > 2:
      last_x, last_y = normalized_vectors[-1]
      if abs(first_x - last_x) < 0.001 and abs(first_y - last_y) < 0.001:
        commands.append('z')

    return ' '.join(commands)

  def _calculate_bounding_box(self, vectors: Sequence[VectorPort]) -> dict[str, float]:
    """Calculate bounding box for vector sequence.

    :param vectors: Sequence of VectorPort objects
    :returns: Dictionary with x, y, width, height
    """
    if not vectors:
      return {'x': 0, 'y': 0, 'width': 100, 'height': 100}

    min_x = min(v.x for v in vectors)
    max_x = max(v.x for v in vectors)
    min_y = min(v.y for v in vectors)
    max_y = max(v.y for v in vectors)

    # Add padding
    padding = 20

    return {
      'x': min_x - padding,
      'y': min_y - padding,
      'width': max_x - min_x + 2 * padding,
      'height': max_y - min_y + 2 * padding,
    }

  def _generate_stencil_style(self, stencil_data: str, metadata: dict[str, Any]) -> str:
    """Generate draw.io stencil style string.

    :param stencil_data: Stencil path data
    :param metadata: Shape metadata
    :returns: Style string for mxCell with stencil
    """
    # Base64 encode the stencil data
    import base64

    stencil_bytes = stencil_data.encode('utf-8')
    stencil_b64 = base64.b64encode(stencil_bytes).decode('ascii')

    # Create stencil shape style
    style_parts = [
      f'shape=stencil({stencil_b64})',
      'whiteSpace=wrap',
      'html=1',
      'fillColor=#dae8fc',
      'strokeColor=#6c8ebf',
      'strokeWidth=2',
      'shadow=1',
      'rounded=0',
      'sketch=1',
      'curveFitting=1',
      'jiggle=1',
      'sketchStyle=comic',
    ]

    # Add gradient
    style_parts.extend(['gradientColor=#7ea6e0', 'gradientDirection=west'])

    # Add custom style from metadata if provided
    if 'style' in metadata:
      custom_style = metadata['style']
      if isinstance(custom_style, dict):
        for key, value in custom_style.items():
          style_parts.append(f'{key}={value}')
      elif isinstance(custom_style, str):
        style_parts.extend(custom_style.split(';'))

    return ';'.join(style_parts) + ';'

  def _prettify_xml(self, element: ET.Element) -> str:
    """Convert XML element to prettified string.

    :param element: XML element
    :returns: Formatted XML string
    """
    # Convert to string first
    rough_string = ET.tostring(element, encoding='unicode')

    # Parse and reformat with indentation
    import xml.dom.minidom

    dom = xml.dom.minidom.parseString(rough_string)

    # Get pretty printed version
    pretty_xml = dom.toprettyxml(indent='  ')

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]

    # Skip XML declaration line
    if lines[0].startswith('<?xml'):
      lines = lines[1:]

    return '\n'.join(lines)

  def create_drawio_file(
    self,
    vectors: Sequence[VectorPort],
    filepath: Path | str,
    metadata: dict[str, Any] | None = None,
  ) -> Path:
    """Create a draw.io file from vector sequence.

    :param vectors: Sequence of VectorPort objects
    :param filepath: Output file path
    :param metadata: Optional shape metadata
    :returns: Path to created file
    """
    filepath = Path(filepath)

    # Ensure .drawio extension
    if not filepath.suffix == '.drawio':
      filepath = filepath.with_suffix('.drawio')

    # Generate XML content
    xml_content = self.vectors_to_drawio(vectors, metadata)

    # Write to file
    filepath.write_text(xml_content, encoding='utf-8')

    return filepath

  def generate_filename(self, shape_type: str, params: dict[str, Any]) -> str:
    """Generate smart filename with parameters and timestamp.

    :param shape_type: Type of shape (e.g., 'dovetail', 'torn_box')
    :param params: Shape parameters
    :returns: Generated filename without extension
    """
    # Start with shape type
    parts = [shape_type]

    # Add key parameters (limit to avoid overly long filenames)
    param_parts = []
    for key, value in sorted(params.items())[:3]:  # Max 3 params
      # Clean parameter name
      clean_key = key.replace('_', '').replace('-', '')

      # Format name
      if isinstance(value, float):
        formatted_value = f'{value:.2f}'.rstrip('0').rstrip('.')
      else:
        formatted_value = str(value)

      param_parts.append(f'{clean_key}{formatted_value}')

    if param_parts:
      parts.extend(param_parts)

    # Add timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    parts.append(timestamp)

    return '_'.join(parts)
