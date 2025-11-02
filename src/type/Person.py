from dataclasses import dataclass
import os
import json

@dataclass(frozen=True)  # Makes it immutable
class Person:
    name: str

    def load_language(self, lang_code: str) -> 'Person':
        """Load person data for the specified language and return new immutable instance"""
        # Get the path to the language-specific sender file
        settings_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'settings', lang_code, 'sender.json'
        )
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            
            return Person(
                name=lang_data.get('name', self.name)
            )
        except (FileNotFoundError, json.JSONDecodeError):
            # Return current instance if language file doesn't exist or is invalid
            return self

