"""Guards and implicit returns on ``async def``, driven by asyncio.run.

Run: poetry run python examples/free_range/08_async_functions.py
See: docs/api-reference.md#guarded_expression
"""

import asyncio

from modgud import CommonGuards, GuardClauseError, guarded_expression


@guarded_expression(CommonGuards.not_empty('user_id'))
async def fetch_user(user_id: str) -> dict[str, str]:
  """Pretend to load a user; the await stands in for real I/O."""
  await asyncio.sleep(0)
  {'id': user_id, 'name': user_id.title()}


@guarded_expression(CommonGuards.in_range(1, 5, 'count'))
async def fetch_many(count: int) -> list[str]:
  """Load ``count`` users concurrently and return their names."""
  users: list[dict[str, str]] = await asyncio.gather(
    *(fetch_user(f'user{n}') for n in range(count))
  )
  [user['name'] for user in users]


async def main() -> None:
  """Run the happy paths and one refusal; the guards fire when the coroutine runs."""
  assert await fetch_user('ada') == {'id': 'ada', 'name': 'Ada'}
  assert await fetch_many(3) == ['User0', 'User1', 'User2']

  refusal: GuardClauseError | None = None
  try:
    await fetch_many(9)
  except GuardClauseError as error:
    refusal = error
  assert str(refusal) == 'count must be between 1 and 5'

  print(f'fetch_many(3) = {await fetch_many(3)}; fetch_many(9) refused: {refusal}')


if __name__ == '__main__':
  asyncio.run(main())
