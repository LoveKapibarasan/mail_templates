

from dataclasses import dataclass

class Gender:
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class Formal:
    FORMAL = "formal"
    INFORMAL = "informal"

@dataclass(frozen=True) 
class Mode:
    """Mode configuration for email templates"""
    gender: str = Gender.NEUTRAL
    formal: str = Formal.FORMAL

class Modes:
    """Container for multiple mode instances"""
    
    def __init__(self):
        self.gender = Gender()
        self.formal = Formal()
    
    def get_available_genders(self):
        """Get all available gender options"""
        return [Gender.MALE, Gender.FEMALE, Gender.NEUTRAL]
    
    def get_available_formal_levels(self):
        """Get all available formality levels"""  
        return [Formal.FORMAL, Formal.INFORMAL]
    
    def create_mode(self, gender=Gender.NEUTRAL, formal=Formal.FORMAL):
        """Create a new Mode instance"""
        return Mode(gender=gender, formal=formal)