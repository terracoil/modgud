"""
Tests for DrawIOManager functionality.

Validates vector to draw.io conversion, coordinate transformation,
file generation, and filename creation.
"""

import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch

import pytest
from modgud.infrastructure.drawio_manager import DrawIOManager
from modgud.util.geo import Vector


class TestDrawIOManager:
  """Test suite for DrawIOManager class."""

  @pytest.fixture
  def manager(self):
    """Create DrawIOManager instance for testing."""
    return DrawIOManager()

  @pytest.fixture
  def simple_vectors(self):
    """Create simple square shape vectors."""
    return [
      Vector(0, 0, name='topLeft'),
      Vector(100, 0, name='topRight'),
      Vector(100, 100, name='bottomRight'),
      Vector(0, 100, name='bottomLeft'),
      Vector(0, 0, name='close'),
    ]

  @pytest.fixture
  def triangle_vectors(self):
    """Create triangle shape vectors."""
    return [
      Vector(50, 0, name='top'),
      Vector(100, 100, name='bottomRight'),
      Vector(0, 100, name='bottomLeft'),
      Vector(50, 0, name='close'),
    ]

  def test_initialization(self):
    """Test DrawIOManager initialization."""
    # Default initialization
    manager = DrawIOManager()
    assert manager.default_width == 800
    assert manager.default_height == 600

    # Custom dimensions
    custom_manager = DrawIOManager(default_width=1200, default_height=800)
    assert custom_manager.default_width == 1200
    assert custom_manager.default_height == 800

  def test_vectors_to_drawio_basic(self, manager, simple_vectors):
    """Test basic vector to draw.io conversion."""
    xml_str = manager.vectors_to_drawio(simple_vectors)

    # Parse XML to validate structure
    root = ET.fromstring(xml_str)

    # Check root element
    assert root.tag == 'mxfile'
    assert root.get('agent') == 'modgud/1.0'

    # Check diagram
    diagram = root.find('diagram')
    assert diagram is not None
    assert diagram.get('name') == 'Shape'

    # Check mxGraphModel
    model = diagram.find('mxGraphModel')
    assert model is not None
    assert model.get('pageWidth') == '800'
    assert model.get('pageHeight') == '600'

  def test_vectors_to_drawio_with_metadata(self, manager, triangle_vectors):
    """Test vector conversion with metadata."""
    metadata = {'name': 'Test Triangle', 'shape_type': 'triangle', 'parameters': {'sides': 3}}

    xml_str = manager.vectors_to_drawio(triangle_vectors, metadata)
    root = ET.fromstring(xml_str)

    # Check diagram name from metadata
    diagram = root.find('diagram')
    assert diagram.get('name') == 'Test Triangle'

  def test_calculate_bounding_box(self, manager, simple_vectors):
    """Test bounding box calculation."""
    bbox = manager._calculate_bounding_box(simple_vectors)

    assert bbox['x'] == -10  # 0 - padding
    assert bbox['y'] == -10  # 0 - padding
    assert bbox['width'] == 120  # 100 + 2*padding
    assert bbox['height'] == 120  # 100 + 2*padding

  def test_calculate_bounding_box_empty(self, manager):
    """Test bounding box with empty vectors."""
    bbox = manager._calculate_bounding_box([])

    assert bbox['x'] == 0
    assert bbox['y'] == 0
    assert bbox['width'] == 100
    assert bbox['height'] == 100

  def test_create_points_string(self, manager, simple_vectors):
    """Test points string creation for polygon."""
    bbox = manager._calculate_bounding_box(simple_vectors)
    points_str = manager._create_points_string(simple_vectors, bbox)

    # Should create normalized coordinates
    assert isinstance(points_str, str)
    assert ' ' in points_str  # Space-separated values

  def test_generate_polygon_style(self, manager):
    """Test polygon style generation."""
    # Default style
    style = manager._generate_polygon_style({})
    assert 'shape=mxgraph.basic.polygon' in style
    assert 'fillColor=#dae8fc' in style
    assert 'strokeColor=#6c8ebf' in style

    # With custom metadata
    metadata = {'style': {'fillColor': '#ff0000', 'strokeWidth': '3'}}
    custom_style = manager._generate_polygon_style(metadata)
    assert 'fillColor=#ff0000' in custom_style
    assert 'strokeWidth=3' in custom_style

  def test_create_poly_coords(self, manager, simple_vectors):
    """Test polyCoords attribute creation."""
    metadata = {'vectors': simple_vectors}
    coords_str = manager._create_poly_coords(metadata)

    # Should be comma-separated normalized coordinates
    assert isinstance(coords_str, str)
    coords = coords_str.split(',')
    assert len(coords) == len(simple_vectors) * 2  # x,y for each vector

  def test_create_drawio_file(self, manager, triangle_vectors, tmp_path):
    """Test draw.io file creation."""
    # Create file
    filepath = tmp_path / 'test_triangle.drawio'
    metadata = {'name': 'Test Triangle'}

    created_path = manager.create_drawio_file(triangle_vectors, filepath, metadata)

    # Verify file exists
    assert created_path.exists()
    assert created_path.suffix == '.drawio'

    # Verify content
    content = created_path.read_text()
    assert '<mxfile' in content
    assert 'Test Triangle' in content

  def test_create_drawio_file_auto_extension(self, manager, simple_vectors, tmp_path):
    """Test that .drawio extension is added automatically."""
    filepath = tmp_path / 'test_shape'  # No extension

    created_path = manager.create_drawio_file(simple_vectors, filepath)

    assert created_path.suffix == '.drawio'
    assert created_path.name == 'test_shape.drawio'

  @patch('modgud.infrastructure.drawio_manager.datetime')
  def test_generate_filename_basic(self, mock_datetime, manager):
    """Test basic filename generation."""
    # Mock datetime
    mock_now = Mock()
    mock_now.strftime.return_value = '20251224_120000'
    mock_datetime.now.return_value = mock_now

    # Test basic filename
    filename = manager.generate_filename('dovetail', {})
    assert filename == 'dovetail_20251224_120000'

  @patch('modgud.infrastructure.drawio_manager.datetime')
  def test_generate_filename_with_params(self, mock_datetime, manager):
    """Test filename generation with parameters."""
    # Mock datetime
    mock_now = Mock()
    mock_now.strftime.return_value = '20251224_120000'
    mock_datetime.now.return_value = mock_now

    # Test with parameters
    params = {'teeth_slope_pct': 0.15, 'teeth_cnt': 3, 'depth': 0.35}

    filename = manager.generate_filename('dovetail', params)

    # Should include first 3 params (sorted) and timestamp
    assert 'dovetail' in filename
    assert '20251224_120000' in filename
    # Check parameter formatting
    assert 'depth0.35' in filename or 'cnt3' in filename

  def test_generate_filename_float_formatting(self, manager):
    """Test float parameter formatting in filenames."""
    params = {
      'value1': 1.0,  # Should become '1'
      'value2': 0.50,  # Should become '0.5'
      'value3': 3.14159,  # Should become '3.14'
    }

    filename = manager.generate_filename('test', params)

    # Check float formatting
    assert 'value11' in filename  # 1.0 -> 1
    assert 'value20.5' in filename  # 0.50 -> 0.5
    assert 'value33.14' in filename  # 3.14159 -> 3.14

  def test_generate_filename_boolean_formatting(self, manager):
    """Test boolean parameter formatting in filenames."""
    params = {'enabled': True, 'disabled': False}

    filename = manager.generate_filename('test', params)

    assert 'disabledn' in filename  # False -> 'n'
    assert 'enabledy' in filename  # True -> 'y'

  def test_xml_structure_validation(self, manager, simple_vectors):
    """Test that generated XML has proper structure."""
    xml_str = manager.vectors_to_drawio(simple_vectors)
    root = ET.fromstring(xml_str)

    # Navigate through expected structure
    diagram = root.find('diagram')
    model = diagram.find('mxGraphModel')
    root_elem = model.find('root')

    # Check for required cells
    cells = root_elem.findall('mxCell')
    assert len(cells) >= 3  # cell0, cell1, and shape cell

    # Check shape cell has geometry
    shape_cell = cells[2]  # Third cell should be the shape
    geometry = shape_cell.find('mxGeometry')
    assert geometry is not None
    assert geometry.get('as') == 'geometry'

    # Check for points array
    points_array = geometry.find('Array[@as="points"]')
    assert points_array is not None

    # Check individual points
    points = points_array.findall('mxPoint')
    assert len(points) == len(simple_vectors)

  def test_coordinate_transformation(self, manager, simple_vectors):
    """Test that coordinates are properly transformed in output."""
    xml_str = manager.vectors_to_drawio(simple_vectors)
    root = ET.fromstring(xml_str)

    # Find points
    points = root.findall('.//mxPoint')

    # First point should be at base position + relative coords
    first_point = points[0]
    # Original (0,0) transformed relative to bbox with offset
    assert first_point.get('x') is not None
    assert first_point.get('y') is not None

    # All points should have valid numeric coordinates
    for point in points:
      x = float(point.get('x'))
      y = float(point.get('y'))
      assert x >= 0
      assert y >= 0
