from dataclasses import dataclass

@dataclass
class EMailComponent:
    lang: Lang
    greeting: str
    body:str
    closing: str
    sender: Person
    receiever: Person
