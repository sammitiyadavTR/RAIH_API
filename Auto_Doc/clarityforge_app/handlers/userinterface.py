from colorama import Fore
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter, WordCompleter, Completer
from rich.console import Console
from rich.markdown import Markdown
import os
import logging

from .preferenceshandler import PreferencesHandler

color_map = {
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "red": Fore.RED,
    "cyan": Fore.CYAN,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
}

class LimitedWordCompleter(Completer):
    def __init__(self, words, limit=10):
        self.word_completer = WordCompleter(words)
        self.limit = limit

    def get_completions(self, document, complete_event):
        completions = self.word_completer.get_completions(document, complete_event)
        for i, completion in enumerate(completions):
            if i >= self.limit:
                break
            yield completion

class UserInterface:
    def __init__(self):
        self.terminal_size = os.get_terminal_size()
        self.path_completer = PathCompleter(expanduser=True)
        self.handler_folder = os.path.dirname(os.path.abspath(__file__))
        with open (os.path.join(self.handler_folder, "data/words_alpha.txt"), "r", encoding='utf-8') as file:
            self.words = file.read().split('\n')
        self.word_completer = LimitedWordCompleter(self.words)

    def get_default_color(self):
        preferences_handler = PreferencesHandler(self)
        preferences = preferences_handler.preferences
        color_name = preferences.get("message_color", "green")
        return color_map.get(color_name, Fore.GREEN)

    def br(self):
        self.terminal_size = os.get_terminal_size()
        print(Fore.CYAN + f"{'='* self.terminal_size.columns}\n")
        logging.debug("Printed separator line")

    def show_message(self, message, color=Fore.GREEN):
        color = self.get_default_color()
        print(color + message)
        logging.debug(f"UI Message: {message}")

    def show_error(self, message):
        print(Fore.RED + message)
        logging.error(f"UI Error: {message}")

    def show_section(self, message, color=Fore.GREEN):
        color = self.get_default_color()
        self.br()
        print(f"{color}{message}\n")
        logging.info(f"UI Section: {message}")
        self.br()

    def stream_message(self, message, color=Fore.GREEN, interactive=True):
        color = self.get_default_color()
        if interactive:
            print(f'{color}{message}', end="", flush=True)
        else:
            print(f'{color}{message}', end='\r', flush=True)
        logging.debug(f"UI Stream: {message[:50]}{'...' if len(message) > 50 else ''}")

    def file_prompt_user(self, message):
        return prompt(f"{message}> ", completer=self.path_completer)
    
    def word_prompt_user(self, message):
        return prompt(f"{message}> ", completer=self.word_completer)
    
    def prompt_user(self, message):
        return prompt(f"{message}> ")

    def show_menu_header(self, version, prerelease=False):
        print(Fore.CYAN + f"ClarityForge {version} Main Menu {'='* (self.terminal_size.columns - len(f'ClarityForge {version} Main Menu '))}\n")
        logging.info(f"Displaying ClarityForge {version} menu")
        if prerelease:
            print(Fore.YELLOW + f"YOU ARE USING A PRERELEASE VERSION OF CLARITY FORGE, use `pip install clarity-forge --force-reinstall` for current stable version.\n")
            logging.warning("User is running a prerelease version")

    def get_directory_size(self, directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    continue
        return total_size

    def convert_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f}{unit}"
            size_bytes /= 1024.0

    def preview_markdown_in_terminal(self, md_content):
        console = Console()
        md = Markdown(md_content)
        console.print(md)
