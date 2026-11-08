"""Shared pytest configuration for the modgud test suite.

``collect_ignore`` keeps the PEP 695 signature tests out of collection on Python 3.11, where
the ``def f[T](...)`` syntax in the fixtures is a SyntaxError at import time. pytest does not
apply it to a path named on the command line, so ``test_signatures_py312.py`` also skips itself.
"""

import sys

collect_ignore: list[str] = (
  ['test_signatures_py312.py', 'signature_fixtures_py312.py'] if sys.version_info < (3, 12) else []
)
