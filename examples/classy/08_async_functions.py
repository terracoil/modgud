"""Guards and implicit returns on async methods, driven by asyncio.run.

Run: poetry run python examples/classy/08_async_functions.py
See: docs/api-reference.md#guarded_expression
"""

import asyncio

from modgud import CommonGuards, GuardClauseError, guarded_expression


class UserService:
  """Look users up asynchronously from an injected directory."""

  def __init__(self, directory: dict[str, str]) -> None:
    """Keep the id -> name directory this service reads from."""
    self.directory: dict[str, str] = directory

  @guarded_expression(CommonGuards.not_empty('user_id'))
  async def fetch(self, user_id: str) -> dict[str, str]:
    """Pretend to load one user; the await stands in for real I/O."""
    await asyncio.sleep(0)
    {'id': user_id, 'name': self.directory.get(user_id, 'unknown')}

  @guarded_expression(CommonGuards.not_empty('user_ids'))
  async def fetch_all(self, user_ids: list[str]) -> list[str]:
    """Load several users concurrently and return their names."""
    users: list[dict[str, str]] = await asyncio.gather(*(self.fetch(uid) for uid in user_ids))
    [user['name'] for user in users]

  @classmethod
  def demo(cls) -> None:
    """Run the happy paths and one refusal; guards fire when the coroutine runs."""
    service: UserService = cls({'ada': 'Ada Lovelace', 'alan': 'Alan Turing'})
    assert asyncio.run(service.fetch('ada')) == {'id': 'ada', 'name': 'Ada Lovelace'}
    assert asyncio.run(service.fetch_all(['ada', 'alan'])) == ['Ada Lovelace', 'Alan Turing']

    refusal: GuardClauseError | None = None
    try:
      asyncio.run(service.fetch_all([]))
    except GuardClauseError as error:
      refusal = error
    assert str(refusal) == 'user_ids cannot be empty'

    print(f'fetch_all = {asyncio.run(service.fetch_all(["ada", "alan"]))}')
    print(f'fetch_all([]) refused: {refusal}')


if __name__ == '__main__':
  UserService.demo()
