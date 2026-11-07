"""The ``eop_`` forms and pattern helpers the implicit-return rewrite recognises."""

from enum import StrEnum

__all__ = ['EopFormEnum']


class EopFormEnum(StrEnum):
  """One member per ``eop_`` name; the value is the public spelling.

  The three forms double as Idunn adapter keys for ``EopPort``.
  """

  COND = 'eop_cond'
  CASE = 'eop_case'
  MATCH = 'eop_match'
  WHEN = 'eop_when'
  VAR = 'eop_var'
  CLAUSE = 'eop_clause'
