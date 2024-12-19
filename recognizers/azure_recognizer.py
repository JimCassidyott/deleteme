"""
Azure Speech Recognition Wrapper.

This module provides a wrapper around Azure's Speech Services SDK to simplify
continuous speech recognition. It handles the configuration and management of
the speech recognition service while providing a simple callback interface
for handling recognized speech.

Note:
    Requires Azure Speech Services credentials to be provided via environment variables:
    - SPEECH_KEY: Azure Speech Service subscription key
    - SPEECH_REGION: Azure region (e.g., 'eastus')
"""

import os
import sys
import json
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
from typing import Callable, List
from .base_recognizer import BaseRecognizer

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AzureRecognizer(BaseRecognizer):
    """
    A wrapper class for Azure's Speech Recognition service.
    
    This class implements the BaseRecognizer interface using Azure's Speech Services.
    It provides continuous speech recognition with callback functionality
    for handling recognized speech.
    
    Attributes:
        callback (Callable[[str], None]): Function called with recognized speech
        speech_config (speechsdk.SpeechConfig): Azure speech service configuration
        speech_recognizer (speechsdk.SpeechRecognizer): The speech recognition engine
    """
    
    def __init__(self, callback: Callable[[str], None]):
        """
        Initialize the Azure Speech Recognizer.
        
        Args:
            callback (Callable[[str], None]): Function to call with recognized text
        
        Raises:
            ValueError: If required environment variables are missing or invalid
        """
        super().__init__(callback)
        
        # Load environment variables, looking in the PyInstaller temp directory if needed
        env_path = get_resource_path('.env')
        load_dotenv(env_path)
        
        # Get Azure credentials from environment
        speech_key = os.getenv('SPEECH_KEY')
        speech_region = os.getenv('SPEECH_REGION')
        
        if not speech_key or not speech_region:
            raise ValueError(
                "Missing required environment variables. Please ensure SPEECH_KEY "
                "and SPEECH_REGION are set in your .env file"
            )
        
        # Configure the speech service
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        self.speech_config.speech_recognition_language = "en-US"
        
        # Enable profanity in transcription
        self.speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
        
        # Disable automatic punctuation
        self.speech_config.set_service_property(
            name='punctuation',
            value='none',
            channel=speechsdk.ServicePropertyChannel.UriQueryParameter
        )
        
        # Create the speech recognizer
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)
        
        # Set up the callback
        self.speech_recognizer.recognized.connect(self._handle_result)
        
        # Load and add phrases from JSON
        self._load_phrases_from_json()
    
    def _load_phrases_from_json(self) -> None:
        """
        Load phrases from the JSON file and add them to the phrase list grammar.
        
        The JSON file should have a "Phrases" array containing strings.
        Raises:
            FileNotFoundError: If the phrases.json file cannot be found
            json.JSONDecodeError: If the JSON file is invalid
            KeyError: If the JSON file doesn't have a "Phrases" key
        """
        json_path = get_resource_path(os.path.join('files', 'phrase.json'))
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                if "Phrases" in data:
                    self.add_phrases(data["Phrases"])
                else:
                    raise KeyError("JSON file must contain a 'Phrases' key")
        except FileNotFoundError:
            print(f"Warning: Could not find phrases file at {json_path}")
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in phrases file at {json_path}")
        except KeyError as e:
            print(f"Warning: {str(e)}")
    
    def add_phrases(self, phrases: List[str]) -> None:
        """
        Add phrases to the recognition grammar to improve recognition accuracy.
        
        This method adds a list of phrases that the speech recognizer should
        listen for specifically. This can improve recognition accuracy for
        specific commands or domain-specific terminology.
        
        Args:
            phrases (List[str]): List of phrases to add to the grammar
        """
        phrase_list_grammar = speechsdk.PhraseListGrammar.from_recognizer(self.speech_recognizer)
        for phrase in phrases:
            phrase_list_grammar.addPhrase(phrase)
    
    def _handle_result(self, evt) -> None:
        """
        Internal handler for speech recognition results.
        
        Args:
            evt (speechsdk.SpeechRecognitionEventArgs): Recognition event arguments
        """
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            # Pass the recognized text to the callback
            self.callback(text)
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print(f"No speech could be recognized: {evt.result.no_match_details}")
    
    def start(self) -> None:
        """Start continuous speech recognition."""
        self.speech_recognizer.start_continuous_recognition()
    
    def stop(self) -> None:
        """Stop speech recognition completely."""
        self.speech_recognizer.stop_continuous_recognition()
