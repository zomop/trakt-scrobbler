import base64
import json
from pathlib import Path

from trakt_scrobbler.app_dirs import DATA_DIR

ID = b'YWIwMTMzYTIzNjViMmM2NGQ3MGZkMmFkZjNjN2U3NzVhNDEzMTQ3MWI1NjM0MDkzMzMzNWFmMWI5NDc4NWEzYQ=='
SECRET = b'YjU3NGFjZDU4NTczMTBmY2RjMWUxOTVjNTk1Mzc5NWZjNjFhMWQ4OWQ2OWZlYzE2NDk2MjRkNTRjYjY2NjIyMg=='


def get_id():
    return base64.b64decode(ID).decode('utf-8')


def get_secret():
    return base64.b64decode(SECRET).decode('utf-8')


def _read_credentials(path: Path) -> tuple[str, str]:
    try:
        with path.open(encoding='utf-8') as secrets_file:
            credentials = json.load(secrets_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'Could not read Trakt credentials from {path}') from exc

    client_id = credentials.get('client_id') if isinstance(credentials, dict) else None
    client_secret = (
        credentials.get('client_secret') if isinstance(credentials, dict) else None
    )
    if not isinstance(client_id, str) or not client_id:
        raise ValueError(f'Trakt credentials in {path} need a non-empty client_id')
    if not isinstance(client_secret, str) or not client_secret:
        raise ValueError(f'Trakt credentials in {path} need a non-empty client_secret')
    return client_id, client_secret


def get_credentials(secrets_file: str | None = None) -> tuple[str, str]:
    """Return configured Trakt credentials, falling back to the bundled pair.

    An explicit path is authoritative and raises a helpful error when invalid.
    Without one, the conventional data-directory file is used only when it
    exists, preserving the existing bundled-credential behavior by default.
    """
    path = (
        Path(secrets_file).expanduser()
        if secrets_file
        else DATA_DIR / 'trakt_secrets.json'
    )
    if path.is_file():
        return _read_credentials(path)
    if secrets_file:
        raise ValueError(f'Trakt credentials file does not exist: {path}')
    return get_id(), get_secret()
