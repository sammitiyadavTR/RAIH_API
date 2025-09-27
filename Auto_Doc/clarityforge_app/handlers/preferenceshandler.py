import json
import os
from pathlib import Path
from colorama import Fore

from .menuhandler import MenuHandler

PREFERENCE_SCHEMA = {
    "validator_runs": {
        "value": 3,
        "type": int,
        "prompt": "Enter the number of validator runs",
    },
    "chat_history_length": {
        "value": 10,
        "type": int,
        "prompt": "Enter the chat history length",
    },
    "enable_reasoning": {
        "value": True,
        "options": [True, False],
        "type": bool,
        "prompt": "Enable reasoning?",
    },
    "message_color": {
        "value": "green",
        "options": ["green", "yellow", "red", "cyan", "blue", "magenta"],
        "type": str,
        "prompt": "Select the message color",
    },
}

class PreferencesHandler:
    def __init__(self, ui):
        self.ui = ui
        self.menu_handler = MenuHandler()
        self.config_dir = Path.home() / ".clarity-forge"
        self.config_file = self.config_dir / "config.json"
        self.preferences = self.load_preferences()

    def load_preferences(self):
        try:
            with open(self.config_file, "r") as f:
                prefs = json.load(f)
        except FileNotFoundError:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            prefs = self.default_preferences()
            self.save_preferences(prefs)

        # Merge with defaults to ensure all keys are present
        defaults = self.default_preferences()
        updated = False
        for key, value in defaults.items():
            if key not in prefs:
                prefs[key] = value
                updated = True
        if updated:
            self.save_preferences(prefs)
        return prefs

    def save_preferences(self, preferences):
        with open(self.config_file, "w") as f:
            json.dump(preferences, f, indent=4)

    def get_preference(self, key, default=None):
        self.preferences = self.load_preferences()
        return self.preferences.get(key, default)

    def set_preference(self, key, value):
        self.preferences[key] = value
        self.save_preferences(self.preferences)

    def default_preferences(self):
        return {k: v["value"] for k, v in PREFERENCE_SCHEMA.items()}

    def configure_preferences(self):
        import questionary

        while True:
            self.ui.br()
            menu_options = [
                f"⚙️ {key.replace('_', ' ').capitalize()}: {self.preferences.get(key)}"
                for key in PREFERENCE_SCHEMA.keys()
            ]
            menu_options.append("🟢 Save and Exit")
            choice = self.menu_handler.select_menu(menu_options, "Select a preference to modify:")
            if choice == "exit" or "Save and Exit" in choice:
                self.ui.show_message("Preferences saved successfully.\n")
                break

            selected_key = None
            for key in PREFERENCE_SCHEMA.keys():
                if f"{key.replace('_', ' ').capitalize()}" in choice:
                    selected_key = key
                    break
            if not selected_key:
                continue
            
            self.ui.show_message("")
            self.ui.br()

            schema = PREFERENCE_SCHEMA[selected_key]
            current_value = self.preferences[selected_key]
            prompt = schema.get("prompt", selected_key)

            if "options" in schema:
                # Use select for options
                options = [str(opt) for opt in schema["options"]]
                default = str(current_value)
                answer = questionary.select(
                    f"{prompt} (current: {default})", choices=options, default=default, qmark="🟠"
                ).ask()
                if answer == "exit" or answer is None:
                    continue
                value = answer if schema["type"] != bool else (answer == "True" or answer == "true")
            else:
                # Use text input for free-form
                default = (
                    ",".join(current_value) if isinstance(current_value, list) else str(current_value)
                )
                answer = questionary.text(f"{prompt} (current: {default})", default=default, qmark="🟠").ask()
                if answer == "exit" or answer is None:
                    continue
                if schema["type"] == int:
                    try:
                        value = int(answer)
                    except ValueError:
                        self.ui.show_message("Invalid input. Please enter an integer.", Fore.RED)
                        continue
                elif schema["type"] == list:
                    value = [p.strip() for p in answer.split(",")]
                else:
                    value = answer
            self.ui.show_message("")

            self.set_preference(selected_key, value)