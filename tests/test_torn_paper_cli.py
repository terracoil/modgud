"""Tests for TornPaper CLI integration via shapetools."""

import subprocess
import sys
from pathlib import Path


class TestTornPaperCLI:
  """Test cases for TornPaper CLI integration."""

  def test_torn_box_help(self):
    """Test that torn-box command shows help information."""
    result = subprocess.run(
      [sys.executable, 'bin/shapetools', 'shape', 'torn-box', '--help'],
      capture_output=True,
      text=True,
      cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    assert 'Generate a torn paper box with specified torn edges' in result.stdout
    assert '--torn-sides' in result.stdout
    assert '--amplitude' in result.stdout
    assert '--segments' in result.stdout

  def test_torn_box_basic_execution(self):
    """Test basic torn-box command execution."""
    result = subprocess.run(
      [
        sys.executable,
        'bin/shapetools',
        'shape',
        'torn-box',
        '--segments',
        '10',  # Use minimum segments for faster test
        '--amplitude',
        '2.0',
      ],
      capture_output=True,
      text=True,
      cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    assert 'Torn Paper Box' in result.stdout
    assert '<path>' in result.stdout
    assert '<move x=' in result.stdout
    assert '<line x=' in result.stdout

  def test_torn_box_with_different_sides(self):
    """Test torn-box with different torn sides."""
    test_cases = ['N', 'S', 'E', 'W', 'NS', 'EW', 'NSEW']

    for sides in test_cases:
      result = subprocess.run(
        [
          sys.executable,
          'bin/shapetools',
          'shape',
          'torn-box',
          '--torn-sides',
          sides,
          '--segments',
          '10',  # Minimum for speed
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
      )

      assert result.returncode == 0, f'Failed for torn-sides={sides}'
      assert f'Torn Paper Box (sides={sides}' in result.stdout
      assert '<path>' in result.stdout

  def test_torn_box_with_custom_parameters(self):
    """Test torn-box with custom parameters."""
    result = subprocess.run(
      [
        sys.executable,
        'bin/shapetools',
        'shape',
        'torn-box',
        '--width',
        '200',
        '--height',
        '150',
        '--segments',
        '15',
        '--amplitude',
        '8.0',
        '--seed',
        '123',
      ],
      capture_output=True,
      text=True,
      cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    assert 'amplitude=8.0, seed=123' in result.stdout
    assert '<path>' in result.stdout

  def test_torn_box_invalid_parameters(self):
    """Test torn-box with invalid parameters."""
    # Test invalid segments (too low)
    result = subprocess.run(
      [
        sys.executable,
        'bin/shapetools',
        'shape',
        'torn-box',
        '--segments',
        '5',  # Below minimum of 10
      ],
      capture_output=True,
      text=True,
      cwd=Path(__file__).parent.parent,
    )

    assert result.returncode != 0
    # Error could be in stdout or stderr
    error_output = result.stdout + result.stderr
    assert 'segments must be between 10 and 1000' in error_output

  def test_torn_box_invalid_sides(self):
    """Test torn-box with invalid torn sides."""
    result = subprocess.run(
      [
        sys.executable,
        'bin/shapetools',
        'shape',
        'torn-box',
        '--torn-sides',
        'XYZ',  # Invalid characters
        '--segments',
        '10',
      ],
      capture_output=True,
      text=True,
      cwd=Path(__file__).parent.parent,
    )

    assert result.returncode != 0
    # Error could be in stdout or stderr
    error_output = result.stdout + result.stderr
    assert "torn_sides must contain only 'N', 'S', 'E', 'W' characters" in error_output

  def test_torn_box_deterministic_output(self):
    """Test that same seed produces consistent output."""
    cmd = [
      sys.executable,
      'bin/shapetools',
      'shape',
      'torn-box',
      '--seed',
      '42',
      '--segments',
      '10',
      '--torn-sides',
      'N',
    ]

    # Run the command twice
    result1 = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    result2 = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)

    assert result1.returncode == 0
    assert result2.returncode == 0
    # Output should be identical
    assert result1.stdout == result2.stdout

  def test_torn_box_different_seeds(self):
    """Test that different seeds produce different output."""
    cmd_base = [
      sys.executable,
      'bin/shapetools',
      'shape',
      'torn-box',
      '--segments',
      '10',
      '--torn-sides',
      'N',
    ]

    result1 = subprocess.run(
      cmd_base + ['--seed', '42'],
      capture_output=True,
      text=True,
      cwd=Path(__file__).parent.parent,
    )
    result2 = subprocess.run(
      cmd_base + ['--seed', '123'],
      capture_output=True,
      text=True,
      cwd=Path(__file__).parent.parent,
    )

    assert result1.returncode == 0
    assert result2.returncode == 0
    # Output should be different
    assert result1.stdout != result2.stdout
