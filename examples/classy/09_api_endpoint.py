"""The README's API endpoint as an instance method with an injected store; failures become a 400.

Run: poetry run python examples/classy/09_api_endpoint.py
See: docs/api-reference.md#guardfailureenum
"""

import hashlib
from typing import Any

from modgud import CommonGuards, GuardFailureEnum, guarded_expression


class UserApi:
  """Create users in whatever dict-like store it is given."""

  def __init__(self, store: dict[int, dict[str, Any]]) -> None:
    """Inject the store; a real app would pass a repository here."""
    self.store: dict[int, dict[str, Any]] = store

  @staticmethod
  def username_length(*args: Any, **kwargs: Any) -> bool | str:
    """Refuse usernames outside 3-20 characters (``username`` is argument 2, after ``self``)."""
    username: str = kwargs.get('username', args[2] if len(args) > 2 else '')
    return 3 <= len(username) <= 20 or 'username must be 3-20 characters'

  @staticmethod
  def bad_request(errors: list[str], *args: Any, **kwargs: Any) -> dict[str, Any]:
    """CALL_HANDLER target: shape the collected failures as an HTTP 400 body."""
    return {'status': 400, 'errors': errors}

  @guarded_expression(
    CommonGuards.not_empty('email'),
    CommonGuards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', 'email'),
    CommonGuards.type_check(int, 'age', position=1),
    CommonGuards.in_range(13, 120, 'age', position=1),
    CommonGuards.not_empty('username', position=2),
    username_length,
    CommonGuards.not_empty('password', position=3),
    continuance=6,
    strategy=GuardFailureEnum.CALL_HANDLER,
    on_failure=bad_request,
  )
  def create_user(self, email: str, age: int, username: str, password: str) -> dict[str, Any]:
    """Create a user; by the time this body runs, every field has been checked."""
    user_id: int = len(self.store) + 1
    password_hash: str = hashlib.sha256(password.encode()).hexdigest()
    self.store[user_id] = {'email': email, 'age': age, 'username': username, 'hash': password_hash}
    {'status': 201, 'user_id': user_id}  # noqa: B018 - implicit return

  @classmethod
  def demo(cls) -> None:
    """Create one user, reject another, and check the store only saw the first."""
    store: dict[int, dict[str, Any]] = {}
    api: UserApi = cls(store)
    created: dict[str, Any] = api.create_user('ada@example.com', 36, 'ada', 'correct horse')
    assert created == {'status': 201, 'user_id': 1}
    assert store[1]['username'] == 'ada' and store[1]['hash'] != 'correct horse'

    rejected: dict[str, Any] = api.create_user('not-an-email', 9, 'al', '')
    assert rejected['status'] == 400
    assert rejected['errors'][1:] == [
      'age must be between 13 and 120',
      'username must be 3-20 characters',
      'password cannot be empty',
    ]
    assert len(store) == 1  # the body never ran for the bad request

    print(f'created: {created}')
    print('rejected:', *rejected['errors'], sep='\n  ')


if __name__ == '__main__':
  UserApi.demo()
