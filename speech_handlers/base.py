"""
Base class for speech handlers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
import pyautogui

# Configure PyAutoGUI safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Add small delay between PyAutoGUI commands

class ListeningState(Enum):
    """Enum for tracking the listening state."""
    LISTENING = auto()
    PAUSED = auto()
    STOPPED = auto()

class BaseSpeechHandler(ABC):
    """
    Base class for speech handlers.
    
    This abstract class defines the interface that all speech handlers must implement.
    It provides basic state management and abstract methods for handling speech input.
    """
    
    def __init__(self):
        """Initialize the speech handler with default state."""
        self.state = ListeningState.LISTENING
    
    @abstractmethod
    def handle_speech(self, text: str) -> str:
        """
        Handle incoming speech text.
        
        Args:
            text (str): The recognized speech text to process
            
        Returns:
            str: The processed text, which may be modified by the handler
        """
        pass
    
    def format_timestamp(self) -> str:
        """Get current timestamp formatted for logging."""
        return datetime.now().strftime("%H:%M:%S")
