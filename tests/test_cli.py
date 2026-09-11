import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from links.cli import main
from links.models import Action, Card, Folder, LinksDocument
from links.storage import ConfigStore


class CliTests(unittest.TestCase):
    def test_search_prints_matching_action_path(self) -> None:
        with TemporaryDirectory() as directory:
            store = ConfigStore(Path(directory))
            store.save(
                LinksDocument(
                    folders=[
                        Folder(
                            title="Work",
                            cards=[
                                Card(
                                    title="Deploy",
                                    actions=[
                                        Action(
                                            title="Dashboard",
                                            action_type="url",
                                            value="https://example.com",
                                        )
                                    ],
                                )
                            ],
                        )
                    ]
                )
            )
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        "--config-home",
                        directory,
                        "--search",
                        "example.com",
                    ]
                )

        self.assertEqual(result, 0)
        self.assertIn("Work/Deploy/Dashboard: https://example.com", output.getvalue())


if __name__ == "__main__":
    unittest.main()