import asyncio
import copy
import yaml

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static
from textual import events

import fantastic_spelling.voice as voice


def load_word_list():
    word_path = Path(Path.home(), "words.yaml")
    if not word_path.is_file():
        raise RuntimeError(f"Can't open the word list at : {word_path}")
    with open(word_path, "r") as word_file:
        word_list = yaml.safe_load(word_file)
    return word_list


class Say(Message):
    def __init__(self, sender: MessageTarget, text: str, queue=False) -> None:
        self.text = text
        self.queue = queue
        super().__init__(sender)


class ResultDisplay(Static):
    "to display the current guess"

    # result_str = reactive("• • •")
    result_str = reactive("•")

    def log_error(self) -> bool:
        self.result_str = self.result_str.replace("•", "❌", 1)

        if self.result_str[-1] == "❌":
            return True
        return False

    def log_pass(self) -> None:
        self.result_str = self.result_str.replace("•", "✅", 1)

    def render(self) -> str:
        return f"{self.result_str}"


class WordDisplay(Static):
    "display the current wrong/right guesses."

    word = reactive("")
    cursor = reactive(True)

    def render(self) -> str:
        disp_txt = self.word
        if self.cursor:
            disp_txt += "_"

        return disp_txt


class WordTry(Static):
    def __init__(self, word):
        self._word = word
        self.word_display = WordDisplay(id="word_display")
        super().__init__()

    def on_mount(self):
        self.set_word(self._word)

    def set_active(self):
        self.add_class("active")

    def remove_active(self):
        self.remove_class("active")
        self.add_class("disabled")
        self.query_one(WordDisplay).cursor = False

    def log_error(self) -> bool:
        return self.query_one(ResultDisplay).log_error()

    def log_pass(self) -> bool:
        self.query_one(ResultDisplay).log_pass()

    def get_word(self) -> str:
        return self.word_display.word

    def set_word(self, word) -> None:
        self.word_display.word = word

    def compose(self) -> ComposeResult:
        yield self.word_display
        yield ResultDisplay(id="results")


def spell_word(word):
    long_form = [f", Capital {x}" if x.isupper() else f", {x}" for x in word]
    return "".join(long_form)


class FansticSpellingApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "fs.css"
    BINDINGS = [
        ("space", "say_word", "Say current word"),
        ("enter", "check_word", "Check you have the word correct."),
    ]

    def __init__(self, word_list):
        self.words = word_list
        super().__init__()

    def action_say_word(self) -> None:
        if self._input_ready:
            self.say(self.current_word)

    async def action_check_word(self) -> None:
        if not self._input_ready:
            return

        word_try = self.query_one("WordTry.active")

        guess = word_try.get_word()

        if self.current_word == guess:
            self.say("You are correct!", True)
            word_try.log_pass()
            word_try.remove_active()

        else:
            self.say("You are wrong!", True)

            if not word_try.log_error():
                return

            self.words.insert(0, self.current_word)

            word_try.remove_active()

        if self.words:
            self.next_word()
            return

        self.say("Practice complete, good job mate!", True)

        await voice.speech_finished()

        self.exit("Good Job Ada! Well done!")

    def on_unmount(self) -> None:
        voice.stop()

    def on_mount(self) -> None:
        self.init_tts()
        self.next_word()

    def next_word(self):
        self._input_ready = False
        self.current_word = self.words.pop(0)

        new_word = WordTry(self.current_word)
        new_word.set_active()
        self.query_one("#word_list").mount(new_word)
        new_word.focus()
        new_word.scroll_visible()

        async def word_reset():
            self.say(f"Please spell {self.current_word}.", True)
            voice.say(spell_word(self.current_word), True)
            await voice.speech_finished()
            self._input_ready = True
            new_word.set_word("")

        asyncio.create_task(word_reset())

    def init_tts(self) -> None:
        voice.start()

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(id="word_list")

    def on_key(self, event: events.Key) -> None:
        if self._input_ready:
            if event.character and event.character.isalpha():
                word_try = self.query_one("WordTry.active")

                utter = event.character
                if utter.isupper():
                    utter = f"Capital {utter}"
                self.say(utter, True)
                word = word_try.get_word()
                word += event.character
                word_try.set_word(word)
            elif event.key == "backspace":
                word_try = self.query_one("WordTry.active")
                word = word_try.get_word()
                word = word[:-1]
                word_try.set_word(word)

    def say(self, text, queue=False):
        voice.say(text, queue)

    def on_say(self, message: Say) -> None:
        self.say(message.text, message.queue)


def run():
    word_list = load_word_list()
    app = FansticSpellingApp(word_list)
    app.run()


if __name__ == "__main__":
    run()
