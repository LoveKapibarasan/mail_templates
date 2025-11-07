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
            'greeting_for_name_prefix': lang_data['header'].get('greeting_for_name_prefix', template_vars.get('greeting_for_name_prefix', '')),
            'greeting_for_name_postfix': lang_data['header'].get('greeting_for_name_postfix', template_vars.get('greeting_for_name_postfix', '')),
            'greeting': lang_data['header'].get('greeting', template_vars.get('greeting', ''))
        })
    
    if 'footer' in lang_data:
        template_vars.update({
            'closing': lang_data['footer'].get('closing', template_vars.get('closing', '')),
            'button_text': lang_data['footer'].get('button_text', template_vars.get('button_text', '')),
            'button_link': lang_data['footer'].get('button_link', template_vars.get('button_link', ''))
        })
    
    if 'sender' in lang_data:
        template_vars.update({
            'name': lang_data['sender'].get('name', template_vars.get('name', ''))
        })
    
    # 5.5. Load mode-specific files from settings/lang_code/mode/*.json
    if 'mode' in filled_data:
        mode_dir = os.path.join(lang_dir, 'mode')
        mode_data = filled_data['mode']
        
        # Load gender-specific file (e.g., male.json, female.json, neutral.json)
        if 'gender' in mode_data:
            gender_file = os.path.join(mode_dir, f"{mode_data['gender']}.json")
            if os.path.exists(gender_file):
                with open(gender_file, "r", encoding="utf-8") as f:
                    gender_data = json.load(f)
                    # Override template_vars with gender-specific data
                    template_vars.update(gender_data)
        
        # Load formality-specific file (e.g., formal.json, informal.json)
        if 'formal' in mode_data:
            formal_file = os.path.join(mode_dir, f"{mode_data['formal']}.json")
            if os.path.exists(formal_file):
                with open(formal_file, "r", encoding="utf-8") as f:
                    formal_data = json.load(f)
                    # Override template_vars with formality-specific data
                    template_vars.update(formal_data)
    
    # 6. Render template
    output = jinja_template.render(template_vars)
    
    return output

if __name__ == "__main__":
    # Example usage: render the mail template
    result = template("en", "data.json")
    print("Template rendered successfully!")
    print(f"Output length: {len(result)} characters")

