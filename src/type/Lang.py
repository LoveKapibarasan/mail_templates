from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)  # Makes it immutable
class Lang:
    code: str  # Language code like 'en', 'de', 'jp'
    name: str  # Language name like 'English', 'German', 'Japanese'
    
    def __post_init__(self):
        if not self.code or len(self.code) != 2:
            raise ValueError("Language code must be a 2-character string")
    
    @classmethod
    def from_code(cls, code: str) -> 'Lang':
        """Create Lang instance from language code"""
        lang_names = {
            'en': 'English',
            'de': 'German',
            'jp': 'Japanese'
        }
        name = lang_names.get(code, code.capitalize())
        return cls(code=code, name=name)

@dataclass(frozen=True) 
class Langs:
    """Container for multiple language instances"""
    
    def __post_init__(self):
        # Define available languages
        object.__setattr__(self, '_lang_names', {
            'en': 'English',
            'de': 'German',
            'jp': 'Japanese'
        })
    
    @property
    def lang_names(self):
        """Get the language names dictionary"""
        return getattr(self, '_lang_names', {
            'en': 'English',
            'de': 'German', 
            'jp': 'Japanese'
        })
    
    def get_all_languages(self):
        """Get all available Language instances"""
        return [Lang.from_code(code) for code in self.lang_names.keys()]
    
    def get_language_codes(self):
        """Get all available language codes"""
        return list(self.lang_names.keys())