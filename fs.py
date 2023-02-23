import asyncio

import pyttsx3

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static


class Say(Message):
    def __init__(self, sender: MessageTarget, text: str, queue=False) -> None:
        self.text = text
        self.queue = queue
        super().__init__(sender)


class ResultDisplay(Static):
    "to display the current guess"


class WordDisplay(Static):
    "display the current wrong/right guesses."


class WordTry(Static):
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "say":
            await self.post_message(Say(self, "Do it!"))

    def compose(self) -> ComposeResult:
        yield WordDisplay("hel_", id="word_display")
        yield ResultDisplay("123", id="results")
        yield Button("Say", id="say", variant="success")
        yield Button("Check", id="check", variant="error")


class FansticSpellingApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "fs.css"
    BINDINGS = []

    async def on_mount(self) -> None:
        self.tts = pyttsx3.init()
        self.tts.startLoop(False)

        async def pump_tts():
            while True:
                if self.tts.isBusy():
                    self.tts.iterate()
                await asyncio.sleep(0)

        asyncio.create_task(pump_tts())

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(WordTry())

    def on_say(self, message: Say) -> None:
        if self.tts.isBusy() and not message.queue:
            return
        self.tts.say(message.text)


if __name__ == "__main__":
    app = FansticSpellingApp()
    app.run()
