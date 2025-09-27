import questionary
import os
from colorama import Fore

class MenuHandler:
    def __init__(self):
        pass

    def select_menu(self, options, message):
        answer = questionary.select(
            message,
            choices=options,
            qmark="🟠"
        ).ask()
        if answer is None:
            return "exit"
        else:
            return answer

    def get_menu_choices(self):
        return [
            "💬 Interactively create documentation",
            "🤖 Assisted documentation creation", 
            "⚡ Automatically create full project documentation",
            "📝 Create document from template",
            "🟢 Refresh file",
            "🔴 Delete file",
            "🟡 Back"
        ]

    def display_output_files(self, current_model, output_dir):
        output_dir_files = os.listdir(output_dir)
        if "existing_files.json" in output_dir_files:
            output_dir_files.remove("existing_files.json")
        for i in range(len(output_dir_files)):
            output_dir_files[i] = f"📄 {output_dir_files[i]}"
        output_dir_files.append("⚙️ CHANGE ADDITIONAL PREFERENCES")
        output_dir_files.append(f"🟢 CHANGE MODEL (CURRENT: {current_model})")
        output_dir_files.append("🔵 UPLOAD NEW FILE")
        output_dir_files.append("🔴 EXIT")
        return output_dir_files