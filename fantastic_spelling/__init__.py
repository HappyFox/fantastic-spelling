import asyncio
import copy


from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static
from textual import events

import fantastic_spelling.voice as voice

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

    result_str = reactive("• • •")

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
        return self.query_one(WordDisplay).word

    def set_word(self, word) -> None:
        self.query_one(WordDisplay).word = word

    def compose(self) -> ComposeResult:
        yield WordDisplay(id="word_display")
        yield ResultDisplay(id="results")


class FansticSpellingApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "fs.css"
    BINDINGS = [
        ("space", "say_word", "Say current word"),
        ("enter", "check_word", "Check you have the word correct."),
    ]

    def action_say_word(self) -> None:
        self.say(self.current_word)

    async def action_check_word(self) -> None:
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

            long_form = [
                f", Capital {x}" if x.isupper() else f", {x}" for x in self.current_word
            ]
            long_form = "".join(long_form)
            self.say(f"You spell {self.current_word}: {long_form}.", True)

            self.words.append(self.current_word)

            word_try.remove_active()

        if self.words:
            self.next_word()
            return

        self.say("Practice complete, good job mate!", True)

        await voice.speach_finished()

        self.exit("Good Job Ada! Well done!")

    def on_unmount(self) -> None:
        voice.stop()

    def on_mount(self) -> None:
        self.init_tts()
        self.words = copy.copy(WORD_LIST)
        self.next_word()

    def next_word(self):
        self.current_word = self.words.pop(0)
        self.say(f"Please spell {self.current_word}.", True)
        new_word = WordTry()
        new_word.set_active()
        self.query_one("#word_list").mount(new_word)
        new_word.focus()
        new_word.scroll_visible()

    def init_tts(self) -> None:
        voice.start()

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(id="word_list")

    def on_key(self, event: events.Key) -> None:
        if event.character and event.character.isalpha():
            word_try = self.query_one("WordTry.active")
            self.say(event.character, True)
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
    app = FansticSpellingApp()
    app.run()


if __name__ == "__main__":
    run()
