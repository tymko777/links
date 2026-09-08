import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from links.models import Card, Folder, LinksDocument
from links.storage import ConfigStore, StorageError


class StorageTests(unittest.TestCase):
    def test_storage_uses_atomic_json_round_trip(self) -> None:
        with TemporaryDirectory() as directory:
            store = ConfigStore(Path(directory))
            original = LinksDocument(
                folders=[
                    Folder(
                        title="Personal",
                        cards=[Card(title="Home")],
                    )
                ]
            )

            store.save(original)
            loaded = store.load()

        self.assertEqual(loaded, original)
        self.assertEqual(store.path, Path(directory) / "links" / "links.json")

    def test_missing_file_returns_starter_document(self) -> None:
        with TemporaryDirectory() as directory:
            document = ConfigStore(Path(directory)).load()

        self.assertEqual(document.folders[0].title, "Getting Started")

    def test_non_object_json_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            store = ConfigStore(Path(directory))
            store.directory.mkdir(parents=True)
            store.path.write_text("[]", encoding="utf-8")

            with self.assertRaises(StorageError):
                store.load()


if __name__ == "__main__":
    unittest.main()