"""``eop_case`` on methods: Elixir's ``case`` with sequence, mapping and value patterns.

Run: poetry run python examples/classy/14_eop_case.py
See: docs/api-reference.md#eop_case
"""

from modgud import eop_case, eop_clause, eop_var, eop_when, implicit_return


class Router:
  """Turns request tuples into route names."""

  def __init__(self, prefix: str = '/api') -> None:
    """Remember the path prefix routes are reported under."""
    self.prefix: str = prefix

  @implicit_return()
  def route(self, request: object) -> str:
    """Name the route for a ``(method, path)`` request; captures stay inside their clause."""
    eop_case(
      request,
      eop_clause(('GET', eop_var.path), f'read {self.prefix}{eop_var.path}'),
      eop_clause(eop_when(('POST', eop_var.path), eop_var.path.startswith('/admin')), 'forbidden'),
      eop_clause(('POST', eop_var.path), f'write {self.prefix}{eop_var.path}'),
      default='unknown',
    )

  @staticmethod
  @implicit_return()
  def shape(payload: object) -> str:
    """Describe a payload by its shape: mapping, sequence or a literal."""
    eop_case(
      payload,
      eop_clause({'id': eop_var.i, **eop_var.rest}, f'record {eop_var.i} + {len(eop_var.rest)}'),
      eop_clause([eop_var.head, *eop_var._], f'list starting {eop_var.head}'),
      eop_clause(None, 'nothing'),
      default='scalar',
    )

  @classmethod
  @implicit_return()
  def routes(cls, requests: list[object]) -> list[str]:
    """Use ``eop_case`` inside a comprehension."""
    [cls().route(r) for r in requests]

  @classmethod
  def demo(cls) -> None:
    """Exercise every clause once."""
    router: Router = cls()
    assert router.route(('GET', '/users')) == 'read /api/users'
    assert router.route(('POST', '/admin/x')) == 'forbidden'
    assert router.route(('POST', '/users')) == 'write /api/users'
    assert router.route('bad') == 'unknown'
    assert cls.shape({'id': 3, 'a': 1}) == 'record 3 + 1'
    assert cls.shape([9, 8]) == 'list starting 9' and cls.shape(None) == 'nothing'
    assert cls.shape(4.5) == 'scalar'
    assert cls.routes([('GET', '/a'), 1]) == ['read /api/a', 'unknown']

    print(f'route: {router.route(("GET", "/users"))}; {router.route(("POST", "/admin/x"))}')
    print(f'shape: {cls.shape({"id": 3, "a": 1})}; {cls.shape([9, 8])}')


if __name__ == '__main__':
  Router.demo()
