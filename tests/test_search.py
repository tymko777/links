import unittest

from links.models import Action, Card, Folder, LinksDocument
from links.search import cards_matching, search_document


class SearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = LinksDocument(
            folders=[
                Folder(
                    title="Projects",
                    cards=[
                        Card(
                            title="Release",
                            favorite=True,
                            tags=["shipping"],
                            actions=[
                                Action(
                                    title="Issue tracker",
                                    action_type="url",
                                    value="https://linear.app",
                                )
                            ],
                        )
                    ],
                )
            ]
        )

    def test_search_finds_tags_and_action_values(self) -> None:
        self.assertEqual(len(search_document(self.document, "shipping")), 1)
        self.assertEqual(len(search_document(self.document, "linear")), 1)
        self.assertEqual(search_document(self.document, "missing"), [])

    def test_search_is_case_insensitive(self) -> None:
        self.assertEqual(len(search_document(self.document, "PROJECTS")), 1)

    def test_folder_match_keeps_all_cards_visible(self) -> None:
        matching = cards_matching(self.document, self.document.folders[0], "projects")
        self.assertEqual([card.title for card in matching], ["Release"])

    def test_card_match_filters_cards(self) -> None:
        folder = self.document.folders[0]
        folder.cards.append(Card(title="Planning"))

        matching = cards_matching(self.document, folder, "release")

        self.assertEqual([card.title for card in matching], ["Release"])

    def test_favorites_filter_keeps_only_favorite_cards(self) -> None:
        folder = self.document.folders[0]
        folder.cards.append(Card(title="Planning"))

        matching = cards_matching(self.document, folder, "", favorites_only=True)

        self.assertEqual([card.title for card in matching], ["Release"])


if __name__ == "__main__":
    unittest.main()