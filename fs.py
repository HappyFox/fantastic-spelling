from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static


class ResultDisplay(Static):
    "to display the current guess"


class WordDisplay(Static):
    "display the current wrong/right guesses."


class WordTry(Static):
    def compose(self) -> ComposeResult:
        yield WordDisplay("hel_", id="word_display")
        yield ResultDisplay("123", id="results")
        yield Button("Say", id="say", variant="success")
        yield Button("Check", id="check", variant="error")


class FansticSpellingApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "fs.css"
    BINDINGS = []

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(WordTry())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = FansticSpellingApp()
    app.run()
