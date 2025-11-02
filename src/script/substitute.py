# References
# https://jinja.palletsprojects.com/en/stable/
# https://omomuki-tech.com/archives/1370

from jinja2 import Environment, FileSystemLoader
import os
import json
from pathlib import Path
import sys
from datetime import datetime

# Add the type directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'type'))

from Person import Person
from Header import Header
from Footer import Footer
from EMailComponent import EMailComponent
from Lang import Lang

def template(lang_code: str, filled_data_file_path: str) -> str:
    # Get the absolute path to templates directory
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
    
    # 1. Environment creation and setup
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # 2. Load template (specify filename)
    jinja_template = env.get_template('mail_template.html')
    
    # 3. Load filled_data_file
    settings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings', filled_data_file_path)
    with open(settings_path, "r", encoding="utf-8") as f:
        filled_data = json.load(f)
    
    # 4. Load language-specific files from settings/lang_code/*.json
    lang_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'settings', lang_code)
    lang_data = {}
    
    # Load header.json, footer.json, sender.json from lang_code directory
    for file_name in ['header.json', 'footer.json', 'sender.json']:
        lang_file_path = os.path.join(lang_dir, file_name)
        if os.path.exists(lang_file_path):
            with open(lang_file_path, "r", encoding="utf-8") as f:
                file_data = json.load(f)
                # Merge into lang_data with file prefix
                base_name = file_name.replace('.json', '')
                lang_data[base_name] = file_data
    
    # 5. Combine filled_data + lang_data
    template_vars = {
        **filled_data,  # Base data from filled_data_file
        **lang_data,    # Language-specific data
        'year': str(datetime.now().year)
    }
    
    # Update specific fields with language data if available
    if 'header' in lang_data:
        template_vars.update({
            'imageURL': lang_data['header'].get('imageURL', template_vars.get('imageURL', '')),
            'greeting': lang_data['header'].get('greeting', template_vars.get('greeting', ''))
        })
    
    if 'footer' in lang_data:
        template_vars.update({
            'closing': lang_data['footer'].get('closing', template_vars.get('closing', ''))
        })
    
    if 'sender' in lang_data:
        template_vars.update({
            'name': lang_data['sender'].get('name', template_vars.get('name', ''))
        })
    
    # 6. Render template
    output = jinja_template.render(template_vars)
    
    return output

if __name__ == "__main__":
    # Example usage: render the mail template
    result = template("en", "data.json")
    print("Template rendered successfully!")
    print(f"Output length: {len(result)} characters")

