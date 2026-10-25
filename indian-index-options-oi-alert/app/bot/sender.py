from typing import Protocol


class AlertSender(Protocol):
    async def send_message(self, chat_id: int, text: str) -> None:
        """Send a message to a Telegram chat."""


class MockAlertSender:
    """Print messages instead of contacting Telegram."""

    async def send_message(self, chat_id: int, text: str) -> None:
        print(f"\n--- MOCK TELEGRAM MESSAGE (chat {chat_id}) ---")
        print(text)
        print("--- END MESSAGE ---\n")