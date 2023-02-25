import asyncio
import copy

import pyttsx3

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static


WORD_LIST = [
    "March",
    "horse",
    "store",
    "large",
    "October",
    "forty",
    "before",
    "north",
    "fourteen",
    "climb",
    "prove",
    "fourth",
]


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
    def compose(self) -> ComposeResult:
        yield WordDisplay("_333", id="word_display")
        yield ResultDisplay("• • •", id="results")


class FansticSpellingApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "fs.css"
    BINDINGS = [("space", "say_word", "Say current word")]

    def action_say_word(self) -> None:
        if self.tts.isBusy():
            return
        self.tts.say(self.current_word)

    def on_mount(self) -> None:
        self.init_tts()
        self.words = copy.copy(WORD_LIST)
        self.add_word()

    def add_word(self):
        self.current_word = self.words.pop(0)
        new_word = WordTry()
        self.query_one("#word_list").mount(new_word)
        new_word.scroll_visible()

    def init_tts(self) -> None:
        self.tts = pyttsx3.init()
        self.tts.startLoop(False)
        self.tts.setProperty("rate", 120)

        async def pump_tts():
            while True:
                if self.tts.isBusy():
                    self.tts.iterate()
                await asyncio.sleep(0)

        asyncio.create_task(pump_tts())
        self.tts.iterate()

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(id="word_list")

    def on_say(self, message: Say) -> None:
        if self.tts.isBusy() and not message.queue:
            return
        self.tts.say(message.text)


if __name__ == "__main__":
    app = FansticSpellingApp()
    app.run()
