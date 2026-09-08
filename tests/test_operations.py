import unittest

from links.models import Card
from links.operations import move_by_id


class OperationTests(unittest.TestCase):
    def test_move_by_id_reorders_items(self) -> None:
        items = [
            Card(id="one", title="One"),
            Card(id="two", title="Two"),
            Card(id="three", title="Three"),
        ]

        changed = move_by_id(items, "three", "one", lambda item: item.id)

        self.assertTrue(changed)
        self.assertEqual([item.id for item in items], ["three", "one", "two"])

    def test_move_by_id_rejects_unknown_ids_without_mutation(self) -> None:
        items = [Card(id="one", title="One")]

        changed = move_by_id(items, "missing", "one", lambda item: item.id)

        self.assertFalse(changed)
        self.assertEqual([item.id for item in items], ["one"])