"""
Dictation speech handler implementation.

This handler provides pure dictation functionality without any command processing.
It simply outputs the recognized text as-is, making it ideal for transcription tasks.
"""

from datetime import datetime
import json
import os
import sys
from .base import BaseSpeechHandler, ListeningState
import pyautogui
from speech_handlers.helpers import is_indefinite_article

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class DictationSpeechHandler(BaseSpeechHandler):
    """
    A simple dictation-focused speech handler.
    
    This handler implements straightforward text output without any command processing,
    making it ideal for pure dictation tasks like transcription or note-taking.
    """
    
    def __init__(self):
        """Initialize the dictation handler."""
        super().__init__()
        self.last_text = ""
        
        # Load modifier keys and special characters from JSON files
        files_dir = 'files'
        
        # Load modifier keys
        modifier_keys_path = get_resource_path(os.path.join(files_dir, 'modifierkeys.json'))
        with open(modifier_keys_path, 'r', encoding='utf-8') as f:
            self.modifier_keys = json.load(f)
            
        # Load special characters
        special_chars_path = get_resource_path(os.path.join(files_dir, 'Specialcharacters.json'))
        with open(special_chars_path, 'r', encoding='utf-8') as f:
            self.special_chars = json.load(f)
    
    def handle_speech(self, text: str) -> str:
        """
        Handle incoming speech text by processing and executing the commands.
        
        Args:
            text (str): The recognized speech text to process
            
        Returns:
            str: The processed text, possibly modified by command processing
        """
        words = text.lower().split()

        # Check for undo command
        if len(words) == 2 and words[0].lower() in ["leah", "lea", "leeah", "leia", "laya", "layah", "leja", "lejah"] and words[1].lower() == "undo":
            pyautogui.hotkey('ctrl', 'z')
            return ""

        # If the user has instructed the computer to type a punctuation mark,
        # add it to the text. An acceptable phrase would be leah put a period.
        # The indefinite article is also handled here - the user can include it or not.
        if len(words) >= 3 and words[0].lower() in ["leah", "lea", "leeah", "leia", "laya", "layah", "leja", "lejah"] and words[1].lower() in ["put", "puts", "putz"]:
            if is_indefinite_article(words[2]):
                words = words[3:]
            text = ' '.join(words).strip()
    
            if text in self.special_chars:
                text = self.special_chars[text]
            else:
                text=""

        # If the user has instructed the computer to type a punctuation mark,
        # add it to the text.  
        if self.last_text:
            try: 
                if self.last_text.strip()[-1] in ['.', '!', '?']:
                    text = " " + text.capitalize()
                if self.last_text[-1].isalnum() and text.strip()[-1] not in [',', ':', ';'] and text.strip()[-1] not in self.special_chars.values():
                    text = " " + text
            except:
                text = text.capitalize()
                
        pyautogui.typewrite(text)
        self.last_text = text
        return text