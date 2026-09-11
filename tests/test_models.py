import unittest

from links.models import Action, Card, Folder, LinksDocument


class ModelTests(unittest.TestCase):
    def test_round_trip_models(self) -> None:
        document = LinksDocument(
            folders=[
                Folder(
                    title="Work",
                    cards=[
                        Card(
                            title="Deploy",
                            tags=["release"],
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

        restored = LinksDocument.from_dict(document.to_dict())
        self.assertEqual(restored, document)
        self.assertEqual(restored.validate(), [])

    def test_card_has_ten_action_limit(self) -> None:
        card = Card(title="Shortcuts")
        for index in range(10):
            card.add_action(
                Action(
                    title=str(index),
                    action_type="clipboard",
                    value=str(index),
                )
            )

        with self.assertRaisesRegex(ValueError, "at most 10"):
            card.add_action(
                Action(title="11", action_type="url", value="https://x.test")
            )

    def test_duplicate_ids_are_rejected(self) -> None:
        duplicate = "same-id"
        document = LinksDocument(
            folders=[
                Folder(
                    id=duplicate,
                    title="One",
                    cards=[Card(id=duplicate, title="Nested")],
                )
            ]
        )

        self.assertTrue(
            any("Duplicate object ID" in error for error in document.validate())
        )

    def test_card_clone_has_fresh_nested_ids(self) -> None:
        original = Card(
            title="Deploy",
            tags=["release"],
            actions=[
                Action(
                    title="Dashboard",
                    action_type="url",
                    value="https://example.com",
                )
            ],
        )

        clone = original.clone()

        self.assertEqual(clone.title, "Deploy (copy)")
        self.assertNotEqual(clone.id, original.id)
        self.assertNotEqual(clone.actions[0].id, original.actions[0].id)
        self.assertEqual(clone.tags, original.tags)
        self.assertEqual(clone.actions[0].value, original.actions[0].value)
        self.assertEqual(clone.validate(), [])

    def test_unsafe_url_is_rejected_by_model_validation(self) -> None:
        action = Action(
            title="Unsafe",
            action_type="url",
            value="javascript:alert(1)",
        )

        self.assertTrue(any("must use http" in error for error in action.validate()))


if __name__ == "__main__":
    unittest.main()