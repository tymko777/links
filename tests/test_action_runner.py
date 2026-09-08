import unittest
from unittest.mock import Mock, patch

from links.models import Action
from links.services.action_runner import ActionError, ActionRunner


class ActionRunnerTests(unittest.TestCase):
    def test_clipboard_action_writes_exact_value(self) -> None:
        clipboard = Mock()
        action = Action(
            title="Template",
            action_type="clipboard",
            value="Hello, {{name}}!",
        )

        ActionRunner().run(action, clipboard)

        clipboard.set.assert_called_once_with("Hello, {{name}}!")

    def test_url_action_is_delegated_to_uri_service(self) -> None:
        action = Action(
            title="Docs",
            action_type="url",
            value="https://example.com",
        )

        with patch.object(ActionRunner, "_open_uri") as open_uri:
            ActionRunner().run(action)

        open_uri.assert_called_once_with("https://example.com")

    def test_command_action_is_delegated_to_terminal_service(self) -> None:
        action = Action(
            title="Status",
            action_type="command",
            value="printf status",
        )

        with patch.object(ActionRunner, "_open_terminal") as open_terminal:
            ActionRunner().run(action)

        open_terminal.assert_called_once_with("printf status")

    def test_unsafe_uri_is_rejected(self) -> None:
        action = Action(
            title="Unsafe",
            action_type="url",
            value="javascript:alert(1)",
        )

        with self.assertRaises(ActionError):
            ActionRunner().run(action)


if __name__ == "__main__":
    unittest.main()