"""
Leia speech recognition module. This is Leia's ear. It will listen to you and
and manage the agent state. Layout was designed to host multiple agents that
perform multiple tasks. If all goes well with the design it should be extensible
to any number of agents Written in multiple programming languages that use gRPC
to communicate with each other.

This module provides continuous speech recognition functionality using
various speech recognition backends. It handles the initialization and
management of the speech recognition service while providing a simple
interface for handling recognized speech.
"""

import threading
from datetime import datetime
from enum import Enum
from recognizers import AzureRecognizer

from speech_handlers import DefaultSpeechHandler, DictationSpeechHandler

class ListeningState(Enum):
    """Enumeration of possible listening states for the speech recognition system."""
    LISTENING = "listening"  # Actively listening and outputting recognized speech
    PAUSED = "paused"       # Still listening but not outputting recognized speech

class SpeechController:
    """
    Controller for managing continuous speech recognition.
    
    This class coordinates between the speech recognizer and speech handler,
    managing the overall state of the speech recognition system.
    """
    
    def __init__(self):
        """Initialize the speech controller."""
        self.state = ListeningState.LISTENING
        self.done = threading.Event()
        
        # Create the default handler and add dictation to its chain
        self.handler = DefaultSpeechHandler()
        self.handler.add_to_handler_chain(DictationSpeechHandler())
        
        # Initialize the recognizer with our callback
        self.recognizer = AzureRecognizer(self.handle_speech)
    
    def handle_speech(self, text: str):
        """
        Route speech text to the handler.
        
        Args:
            text (str): The recognized speech text to process
        """
        # Use lowercase only for command checking
        command_text = text.lower().strip()
        
        # Handle voice commands
        if command_text == "leah stop":
            print("Stop command received!")
            self.stop()
        elif command_text == "leah pause" and self.state == ListeningState.LISTENING:
            self.pause()
        elif command_text == "leah resume" and self.state == ListeningState.PAUSED:
            self.resume()
        elif self.handler.state == self.handler.state.STOPPED:
            self.done.set()
        # Pass the text to the handler for further processing and output
        self.handler.handle_speech(text)

    def start(self):
        """
        Start the speech recognition system.
        
        Initializes the recognizer and waits for the stop command.
        Prints available commands and handles the main recognition loop.
        """
        print("Starting continuous speech recognition...")
        print("Commands available:")
        print("  - 'Leah pause' to pause listening")
        print("  - 'Leah resume' to resume listening")
        print("  - 'Leah stop' to end the program")
        
        self.recognizer.start()
        
        # Wait for the stop command
        self.done.wait()
        self.recognizer.stop()
        print("Speech recognition stopped.")
    
    def stop(self):
        """Stop speech recognition and signal the system to shut down."""
        self.done.set()
    
    def pause(self):
        """
        Pause speech output.
        
        Recognition continues but recognized speech is not printed.
        Voice commands are still processed.
        """
        self.state = ListeningState.PAUSED
        print("Recognition paused. Say 'Leah resume' to continue...")
    
    def resume(self):
        """Resume speech output after being paused."""
        self.state = ListeningState.LISTENING
        print("Recognition resumed!")

    def run(self):
        """Run the speech recognition loop."""
        try:
            self.recognizer.start()
            self.done.wait()  # Wait until stop command
        finally:
            self.recognizer.stop()

def main():
    """Main entry point for the speech recognition system."""
    controller = SpeechController()
    controller.start()

if __name__ == "__main__":
    main()
