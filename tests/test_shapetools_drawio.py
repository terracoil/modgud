"""
Integration tests for draw.io generation in shapetools CLI.

Tests the end-to-end functionality of generating draw.io files
from various shape commands.
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


class TestShapeToolsDrawIO:
  """Test draw.io generation via shapetools CLI."""

  @pytest.fixture
  def project_root(self):
    """Get project root directory."""
    return Path(__file__).parent.parent

  @pytest.fixture(autouse=True)
  def cleanup_drawio_files(self, project_root):
    """Clean up any generated draw.io files after tests."""
    yield
    # Cleanup after test
    for drawio_file in project_root.glob('*.drawio'):
      if any(
        prefix in drawio_file.name
        for prefix in ['dovetail_', 'torn_box_', 'stackable_', 'noisy_line_', 'trapezoid_']
      ):
        drawio_file.unlink()

    # Clean up test output directory
    test_output = project_root / 'test_drawio_output'
    if test_output.exists():
      for file in test_output.iterdir():
        file.unlink()
      test_output.rmdir()

  def run_shapetools(self, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run shapetools command with given arguments."""
    cmd = [sys.executable, 'bin/shapetools'] + args
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

  def validate_drawio_file(self, filepath: Path) -> bool:
    """Validate that a draw.io file has proper structure."""
    try:
      tree = ET.parse(filepath)
      root = tree.getroot()

      # Check root element
      assert root.tag == 'mxfile'
      assert root.get('agent') == 'modgud/1.0'

      # Check for diagram
      diagram = root.find('diagram')
      assert diagram is not None

      # Check for mxGraphModel
      model = diagram.find('.//mxGraphModel')
      assert model is not None

      # Check for at least one shape cell
      cells = root.findall('.//mxCell[@vertex="1"]')
      assert len(cells) > 0

      return True
    except Exception as e:
      print(f'Validation error: {e}')
      return False

  def test_dovetail_drawio_generation(self, project_root):
    """Test draw.io generation for dovetail joints."""
    # Run command with draw.io flag
    result = self.run_shapetools(
      ['joinery', 'dovetail', '--teeth-slope-pct', '0.2', '--teeth-cnt', '4', '--drawio'],
      project_root,
    )

    # Check command succeeded
    assert result.returncode == 0
    assert '✓ Created draw.io file:' in result.stdout

    # Extract filename from output
    for line in result.stdout.split('\n'):
      if 'Created draw.io file:' in line:
        filename = line.split()[-1]
        break
    else:
      pytest.fail('Could not find draw.io filename in output')

    # Validate the file
    drawio_path = project_root / filename
    assert drawio_path.exists()
    assert self.validate_drawio_file(drawio_path)

  def test_torn_box_drawio_generation(self, project_root):
    """Test draw.io generation for torn paper boxes."""
    result = self.run_shapetools(
      [
        'shape',
        'torn-box',
        '--amplitude',
        '3.0',
        '--segments',
        '20',  # Fewer segments for faster test
        '--seed',
        '42',
        '--drawio',
      ],
      project_root,
    )

    assert result.returncode == 0
    assert '✓ Created draw.io file:' in result.stdout

    # Find the generated file
    drawio_files = list(project_root.glob('torn_box_*.drawio'))
    assert len(drawio_files) >= 1

    # Validate the newest file
    newest_file = max(drawio_files, key=lambda p: p.stat().st_mtime)
    assert self.validate_drawio_file(newest_file)

  def test_stackable_trapezoid_drawio(self, project_root):
    """Test draw.io generation for stackable trapezoids."""
    result = self.run_shapetools(
      ['shape', 'stackable-trapezoid', '--angle', '75', '--notch-height', '0.25', '--drawio'],
      project_root,
    )

    assert result.returncode == 0
    assert '✓ Created draw.io file:' in result.stdout

    # Verify file exists with expected pattern
    drawio_files = list(project_root.glob('stackable_trapezoid_*.drawio'))
    assert len(drawio_files) >= 1
    assert self.validate_drawio_file(drawio_files[0])

  def test_noisy_line_drawio(self, project_root):
    """Test draw.io generation for noisy lines."""
    result = self.run_shapetools(
      [
        'shape',
        'noisy-line',
        '--start-x',
        '10',
        '--start-y',
        '20',
        '--end-x',
        '90',
        '--end-y',
        '80',
        '--amplitude',
        '4.0',
        '--segments',
        '15',
        '--drawio',
      ],
      project_root,
    )

    assert result.returncode == 0
    assert '✓ Created draw.io file:' in result.stdout

    # Check file generation
    drawio_files = list(project_root.glob('noisy_line_*.drawio'))
    assert len(drawio_files) >= 1
    assert self.validate_drawio_file(drawio_files[0])

  def test_trapezoid_demo_drawio(self, project_root):
    """Test draw.io generation for trapezoid demo."""
    result = self.run_shapetools(
      [
        'shape',
        'stackable-trapezoid-demo',
        '--count',
        '2',
        '--angle',
        '75',  # Valid angle between 70-85
        '--drawio',
      ],
      project_root,
    )

    assert result.returncode == 0
    assert '✓ Created draw.io file:' in result.stdout

    # Verify demo file
    drawio_files = list(project_root.glob('trapezoid_demo_*.drawio'))
    assert len(drawio_files) >= 1
    assert self.validate_drawio_file(drawio_files[0])

  def test_custom_output_directory(self, project_root):
    """Test draw.io generation with custom output directory."""
    output_dir = project_root / 'test_drawio_output'

    result = self.run_shapetools(
      ['joinery', 'dovetail', '--drawio', '--drawio-output', str(output_dir)], project_root
    )

    assert result.returncode == 0

    # Check directory was created
    assert output_dir.exists()
    assert output_dir.is_dir()

    # Check file was created in the directory
    drawio_files = list(output_dir.glob('*.drawio'))
    assert len(drawio_files) == 1
    assert self.validate_drawio_file(drawio_files[0])

  def test_drawio_filename_formatting(self, project_root):
    """Test that filenames are properly formatted."""
    result = self.run_shapetools(
      [
        'shape',
        'torn-box',
        '--amplitude',
        '2.5',
        '--torn-sides',
        'NSEW',
        '--seed',
        '999',
        '--segments',
        '10',
        '--drawio',
      ],
      project_root,
    )

    assert result.returncode == 0

    # Find generated file
    drawio_files = list(project_root.glob('torn_box_*.drawio'))
    newest_file = max(drawio_files, key=lambda p: p.stat().st_mtime)

    # Check filename components
    filename = newest_file.name
    assert 'torn_box' in filename
    assert 'amp2.5' in filename  # Float formatting
    assert 'seed999' in filename
    assert 'sidesNSEW' in filename

  def test_drawio_polygon_coordinates(self, project_root):
    """Test that polygon coordinates are properly generated."""
    result = self.run_shapetools(
      ['shape', 'stackable-trapezoid', '--width', '50', '--height', '50', '--drawio'], project_root
    )

    assert result.returncode == 0

    # Parse the generated file
    drawio_files = list(project_root.glob('stackable_trapezoid_*.drawio'))
    assert len(drawio_files) >= 1

    tree = ET.parse(drawio_files[0])
    root = tree.getroot()

    # Find shape cell
    shape_cells = root.findall('.//mxCell[@vertex="1"]')
    assert len(shape_cells) > 0

    # Check style contains polyCoords
    style = shape_cells[0].get('style', '')
    assert 'polyCoords=' in style

    # Check geometry
    geometry = shape_cells[0].find('mxGeometry')
    assert geometry is not None
    assert float(geometry.get('width', '0')) > 0
    assert float(geometry.get('height', '0')) > 0

  def test_multiple_shapes_no_collision(self, project_root):
    """Test that multiple shapes generate unique filenames."""
    # Generate first shape
    result1 = self.run_shapetools(['joinery', 'dovetail', '--drawio'], project_root)
    assert result1.returncode == 0

    # Small delay to ensure different timestamp
    import time

    time.sleep(1)

    # Generate second shape with same parameters
    result2 = self.run_shapetools(['joinery', 'dovetail', '--drawio'], project_root)
    assert result2.returncode == 0

    # Check that we have two different files
    drawio_files = list(project_root.glob('dovetail_*.drawio'))
    assert len(drawio_files) >= 2

    # Verify filenames are different
    filenames = [f.name for f in drawio_files]
    assert len(set(filenames)) == len(filenames)  # All unique

  def test_verbose_mode_drawio_info(self, project_root):
    """Test that verbose mode shows additional draw.io info."""
    result = self.run_shapetools(
      [
        '--verbose',  # Verbose flag
        'shape',
        'noisy-line',
        '--drawio',
      ],
      project_root,
    )

    assert result.returncode == 0
    assert '✓ Created draw.io file:' in result.stdout
    # Verbose mode should show additional info
    assert 'Shape:' in result.stdout
    assert 'Parameters:' in result.stdout
    assert 'Vectors:' in result.stdout
    assert 'points' in result.stdout
