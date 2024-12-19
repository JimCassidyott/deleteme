"""
Default speech handler implementation.
"""

from typing import List
from .base import BaseSpeechHandler, ListeningState

class DefaultSpeechHandler(BaseSpeechHandler):
    """
    Default implementation of speech handling logic.
    
    This handler implements basic command recognition for controlling the speech recognition 
    state (pause, resume, stop). It also manages a chain of speech handlers that can be
    added and removed dynamically.

    This will be the operating system for the intelligent agent. It will manage the loading and unloading 
    of modules that perform different tasks. 
    """
    
    def __init__(self):
        """Initialize the speech handler."""
        super().__init__()
        self._handler_chain: List[BaseSpeechHandler] = []
    
    def add_to_handler_chain(self, handler: BaseSpeechHandler) -> None:
        """
        Add a speech handler to the chain.
        
        Args:
            handler (BaseSpeechHandler): The handler to add to the chain
        
        Raises:
            TypeError: If handler does not inherit from BaseSpeechHandler
        """
        if not isinstance(handler, BaseSpeechHandler):
            raise TypeError("Handler must inherit from BaseSpeechHandler")
        self._handler_chain.append(handler)
    
    def remove_handler(self, handler: BaseSpeechHandler) -> None:
        """
        Remove a speech handler from the chain.
        
        Args:
            handler (BaseSpeechHandler): The handler to remove
        """
        if handler in self._handler_chain:
            self._handler_chain.remove(handler)
    
    def clear_handlers(self) -> None:
        """Remove all speech handlers from the chain."""
        self._handler_chain.clear()
    
    def handle_speech(self, text: str) -> str:
        """
        Handle incoming speech text.
        
        This implementation checks for basic control commands and
        types recognized speech into the active window.
        
        Args:
            text (str): The recognized speech text to process
            
        Returns:
            str: The processed text, possibly modified by command processing
        """
        timestamp = self.format_timestamp()
        
        # Keep original text for display but use lowercase for command checking
        text_lower = text.lower()
        
        # Check for control commands
        if "leah stop" in text_lower:
            print(f"[{timestamp}] Stopping speech recognition")
            self.state = ListeningState.STOPPED
        elif "leah pause" in text_lower:
            print(f"[{timestamp}] Pausing speech recognition")
            self.state = ListeningState.PAUSED
        elif "leah resume" in text_lower:
            print(f"[{timestamp}] Resuming speech recognition")
            self.state = ListeningState.LISTENING
        else:
            # Type recognized text if we're in listening state
            if self.state == ListeningState.LISTENING:
                try:
                    if len(self._handler_chain) > 0:
                        self._handler_chain[0].handle_speech(text)
            
                except Exception as e:
                    print(f"Error processing text: {e}")  # Debug print for errors
                    
        
        return text
