"""The README's API endpoint, complete: every validation failure becomes one 400 payload.

Run: poetry run python examples/free_range/09_api_endpoint.py
See: docs/api-reference.md#guardfailureenum
"""

import hashlib
from typing import Any

from modgud import GuardFailureEnum, Guards, guarded_expression

USERS: dict[int, dict[str, Any]] = {}  # stands in for the database


def username_length(*args: Any, **kwargs: Any) -> bool | str:
  """Refuse usernames outside 3-20 characters (``username`` is argument 2)."""
  username: str = kwargs.get('username', args[2] if len(args) > 2 else '')
  return 3 <= len(username) <= 20 or 'username must be 3-20 characters'


def bad_request(errors: list[str], *args: Any, **kwargs: Any) -> dict[str, Any]:
  """CALL_HANDLER target: shape the collected failures as an HTTP 400 body."""
  return {'status': 400, 'errors': errors}


def save_user(email: str, age: int, username: str, password_hash: str) -> int:
  """Insert a user row and return its id."""
  user_id: int = len(USERS) + 1
  USERS[user_id] = {'email': email, 'age': age, 'username': username, 'hash': password_hash}
  return user_id


@guarded_expression(
  Guards.not_empty('email'),
  Guards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', 'email'),
  Guards.type_check(int, 'age', position=1),
  Guards.in_range(13, 120, 'age', position=1),
  Guards.not_empty('username', position=2),
  username_length,
  Guards.not_empty('password', position=3),
  continuance=6,
  strategy=GuardFailureEnum.CALL_HANDLER,
  on_failure=bad_request,
)
def create_user(email: str, age: int, username: str, password: str) -> dict[str, Any]:
  """Create a user; by the time this body runs, every field has been checked."""
  password_hash: str = hashlib.sha256(password.encode()).hexdigest()
  {'status': 201, 'user_id': save_user(email, age, username, password_hash)}


if __name__ == '__main__':
  created: dict[str, Any] = create_user('ada@example.com', 36, 'ada', 'correct horse')
  assert created == {'status': 201, 'user_id': 1}
  assert USERS[1]['username'] == 'ada' and USERS[1]['hash'] != 'correct horse'

  rejected: dict[str, Any] = create_user('not-an-email', 9, 'al', '')
  assert rejected == {
    'status': 400,
    'errors': [
      'email must match pattern ^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$',
      'age must be between 13 and 120',
      'username must be 3-20 characters',
      'password cannot be empty',
    ],
  }
  assert len(USERS) == 1  # the body never ran for the bad request

  print(f'created: {created}')
  print('rejected:', *rejected['errors'], sep='\n  ')
