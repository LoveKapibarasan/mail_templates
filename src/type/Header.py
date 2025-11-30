from dataclasses import dataclass
import os
import json

@dataclass(frozen=True)  # Makes it immutable
class Header:
    imageURL: str
    greeting: str

    def load_language(self, lang_code: str) -> 'Header':
        """Load header data for the specified language and return new immutable instance"""
        # Get the path to the language-specific header file
        settings_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'settings', lang_code, 'header.json'
        )
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            
            return Header(
                imageURL=lang_data.get('imageURL', self.imageURL),
                greeting=lang_data.get('greeting', self.greeting)
            )
        except FileNotFoundError:
            # Return current instance if language file doesn't exist
            return self
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON Error in file: {settings_path}")
            print(f"[DEBUG] {e}")
            # Return current instance but print error
            return self
