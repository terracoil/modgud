"""``eop_match`` on methods: Elixir's ``match?`` as a boolean expression.

Run: poetry run python examples/classy/15_eop_match.py
See: docs/api-reference.md#eop_match
"""

from modgud import eop_match, eop_var, eop_when, implicit_return


class Inbox:
  """Filters messages written as ``(sender, subject)`` tuples."""

  def __init__(self, owner: str) -> None:
    """Remember whose inbox this is."""
    self.owner: str = owner

  @implicit_return()
  def is_self_note(self, message: object) -> bool:
    """Tell whether ``message`` was sent by the owner; a bare name compares by value."""
    eop_match((self.owner, eop_var._), message)

  @staticmethod
  @implicit_return()
  def is_urgent(message: object) -> bool:
    """Tell whether the subject is marked urgent; the guard reads the capture."""
    eop_match(eop_when((eop_var._, eop_var.subject), eop_var.subject.startswith('URGENT')), message)

  @classmethod
  @implicit_return()
  def urgent(cls, messages: list[object]) -> list[object]:
    """Use ``eop_match`` as a comprehension filter."""
    [m for m in messages if cls.is_urgent(m)]

  @classmethod
  def demo(cls) -> None:
    """Exercise every pattern once."""
    inbox: Inbox = cls('ana')
    assert inbox.is_self_note(('ana', 'remember milk')) and not inbox.is_self_note(('bo', 'hi'))
    assert cls.is_urgent(('bo', 'URGENT: server')) and not cls.is_urgent(('bo', 'lunch?'))
    assert not cls.is_urgent('not a tuple')
    assert cls.urgent([('bo', 'URGENT: x'), ('cy', 'y')]) == [('bo', 'URGENT: x')]

    print(f'self note: {inbox.is_self_note(("ana", "remember milk"))}')
    print(f'urgent: {cls.urgent([("bo", "URGENT: x"), ("cy", "y")])}')


if __name__ == '__main__':
  Inbox.demo()
