import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from trakt_scrobbler import trakt_key_holder
from trakt_scrobbler.trakt_auth import TraktAuth


class TestTraktCredentials(unittest.TestCase):
    def write_credentials(self, directory, data):
        path = Path(directory) / "trakt_secrets.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_uses_explicit_credentials_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_credentials(
                directory, {"client_id": "custom-id", "client_secret": "custom-secret"}
            )

            self.assertEqual(
                trakt_key_holder.get_credentials(str(path)),
                ("custom-id", "custom-secret"),
            )

    def test_uses_default_data_file_when_present(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_credentials(
                directory, {"client_id": "data-id", "client_secret": "data-secret"}
            )
            with patch.object(trakt_key_holder, "DATA_DIR", Path(directory)):
                self.assertEqual(
                    trakt_key_holder.get_credentials(), ("data-id", "data-secret")
                )
            self.assertEqual(path.name, "trakt_secrets.json")

    def test_falls_back_to_bundled_credentials_when_data_file_is_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(trakt_key_holder, "DATA_DIR", Path(directory)):
                self.assertEqual(
                    trakt_key_holder.get_credentials(),
                    (trakt_key_holder.get_id(), trakt_key_holder.get_secret()),
                )

    def test_rejects_missing_explicit_file(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            trakt_key_holder.get_credentials("~/missing-trakt-secrets.json")

    def test_rejects_incomplete_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_credentials(directory, {"client_id": "only-id"})

            with self.assertRaisesRegex(ValueError, "client_secret"):
                trakt_key_holder.get_credentials(str(path))

    def test_trakt_auth_uses_configured_credentials(self):
        config_view = {
            "general": {
                "auth": {
                    "trakt_secrets_file": MagicMock(
                        get=MagicMock(return_value="/tmp/custom-trakt-secrets.json")
                    )
                }
            }
        }
        with (
            patch("trakt_scrobbler.trakt_auth.config", config_view),
            patch(
                "trakt_scrobbler.trakt_auth.trakt_key_holder.get_credentials",
                return_value=("custom-id", "custom-secret"),
            ) as get_credentials,
        ):
            auth = TraktAuth()

        get_credentials.assert_called_once_with("/tmp/custom-trakt-secrets.json")
        self.assertEqual(auth.CLIENT_ID, "custom-id")
        self.assertEqual(auth.CLIENT_SECRET, "custom-secret")


if __name__ == "__main__":
    unittest.main()
