from dataclasses import dataclass, replace
from datetime import datetime
from typing import Optional
from Person import Person
from Header import Header
from Footer import Footer
from Lang import Lang

@dataclass
class EMailComponent:
    lang: Lang
    header: Header
    body: str 
    footer: Footer
    sender: Person 
    receiver: Person 
    time: datetime

    def __post_init__(self):
        # Set default time if not provided
        if self.time is None:
            object.__setattr__(self, 'time', datetime.now())

    @classmethod
    def create_with_defaults(cls, lang_code: str = 'en', body: str = '', receiver_name: str = '') -> 'EMailComponent':
        """Create an EMailComponent with default values"""
        lang = Lang.from_code(lang_code)
        now = datetime.now()
        
        # Create default instances
        header = Header(imageURL="", greeting="")
        footer = Footer(closing="")
        sender = Person(name="")
        receiver = Person(name=receiver_name)
        
        return cls(
            lang=lang,
            header=header,
            body=body,
            footer=footer,
            sender=sender,
            receiver=receiver,
            time=now
        )

    def load_language(self, lang_code: str) -> 'EMailComponent':
        """Load language data for all immutable components and return new instance"""
        new_lang = Lang.from_code(lang_code)
        
        # Load language-specific data for all immutable components
        new_header = self.header.load_language(lang_code)
        new_footer = self.footer.load_language(lang_code)
        new_sender = self.sender.load_language(lang_code)
        
        # Return new instance with updated language components
        return replace(
            self,
            lang=new_lang,
            header=new_header,
            footer=new_footer,
            sender=new_sender
        )
    
    def load_data(self, body: str, receiver: Person) -> 'EMailComponent':
        """Load dynamic data (body and receiver) and return new instance"""
        return replace(
            self,
            body=body,
            receiver=receiver
        )

    def to_template_vars(self) -> dict:
        """Convert the email component to template variables for Jinja2"""
        return {
            'lang_code': self.lang.code,
            'lang_name': self.lang.name,
            'sender_name': self.sender.name,
            'receiver_name': self.receiver.name,
            'header_image': self.header.imageURL,
            'header_greeting': self.header.greeting,
            'footer_closing': self.footer.closing,
            'current_time': self.time.isoformat(),
            'name': self.sender.name,  
            'greeting_text': self.header.greeting,  
            'text': self.body,  
            'closing': self.footer.closing,  
            'image_url': self.header.imageURL,  
            'year': str(self.time.year)  
        }

