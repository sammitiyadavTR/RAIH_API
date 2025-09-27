import os
import json
from colorama import Fore

class ModelHandler:
    def __init__(self):
        self.model_config_path = os.path.expanduser("~/.clarity-forge/model_config.json")
        self.default_config = {
            "selected_model": "Gemini 2.5 Flash",
            "available_models": ["Gemini 2.5 Flash", "Gemini 2.0 Flash", "Claude 3.7 Sonnet", "Claude 4 Sonnet", "Claude 4 Opus", "GPT-4.1", ]
        }
        self.load_config()
        
    def load_config(self):
        if not os.path.exists(self.model_config_path):
            self.set_default_config()
        else:
            with open(self.model_config_path, "r") as f:
                self.config = json.load(f)
                if self.config.get("available_models") != self.default_config["available_models"]:
                    print(self.config.get("available_models"))
                    print(self.default_config["available_models"])
                    self.config["available_models"] = self.default_config["available_models"]
            
    def set_default_config(self):
        os.makedirs(os.path.dirname(self.model_config_path), exist_ok=True)
        with open(self.model_config_path, "w") as f:
            json.dump(self.default_config, f, indent=4)
        self.config = self.default_config

    def save_config(self):
        try:
            if not self.model_config_path:
                raise ValueError("Model config path is not set.")
            
            
            config_json = json.dumps(self.config, indent=4)
            
            with open(self.model_config_path, "w") as f:
                f.write(config_json)
        
        except Exception as e:
            print(f"{Fore.RED}Failed to save model configuration: {e}")
            
    def get_selected_model(self):
        return self.config["selected_model"]
    
    def get_available_models(self):
        return self.config["available_models"]
    
    def set_selected_model(self, model):
        if model in self.config["available_models"]:
            self.config["selected_model"] = model
            self.save_config()
            return True
        return False
    
    def get_workflow_id(self, model_name):
        # Define workflow IDs for each model
        workflow_ids = {
            "Gemini 2.0 Flash": "f3b80ac0-8e14-44ba-a806-d23341098fa8",
            "Claude 3.7 Sonnet": "46d44241-5e9b-4de2-9803-070325514ed8",
            "Gemini 2.5 Flash": "fbafcfa8-80c1-4050-9b26-fddf4c8f6295",
            "Claude 4 Sonnet": "2023f639-e8bc-445e-936b-1af1686038a7",
            "Claude 4 Opus": "9ab6e4c3-ceed-4671-b11d-12c79bddfee9",
            "GPT-4.1": "7296739d-d724-450f-ac1a-1a30cebf22af",
        }
        
        return workflow_ids.get(model_name)
    
    def get_prompt_paths(self, model_name):
        # Define prompt paths for each model
        prompt_paths = {
            "Gemini 2.0 Flash": "gemini_20_flash",
            "Claude 3.7 Sonnet": "claude_37",
            "Gemini 2.5 Flash": "gemini_20_flash",
            "Claude 4 Sonnet": "gemini_20_flash",
            "Claude 4 Opus": "gemini_20_flash",
            "GPT-4.1": "gemini_20_flash",
            # "Gemini 2.5 Flash": "vertexai_gemini-2.5-flash",
            # "Claude 4 Sonnet": "anthropic_direct.claude-v4-sonnet",
            # "Claude 4 Opus": "anthropic_direct.claude-v4-opus",
            # "GPT-4.1": "openai_gpt-41",
        }
        
        return prompt_paths.get(model_name)