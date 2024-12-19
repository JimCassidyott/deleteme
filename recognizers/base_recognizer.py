"""
Abstract base class for speech recognizers.

This module defines the interface that all speech recognizers must implement.
It ensures consistent behavior across different speech recognition implementations.
"""

from abc import ABC, abstractmethod
from typing import Callable

class BaseRecognizer(ABC):
    """
    Abstract base class defining the interface for speech recognizers.
    
    All speech recognizer implementations must inherit from this class
    and implement all abstract methods. This ensures consistent behavior
    across different speech recognition services.

    A recognizer has one job: to recognize speech and call a callback function. It listens
    for speech and passes the recognized text to the callback. 
    
    Attributes:
        callback (Callable[[str], None]): Function called with recognized speech
    """
    
    def __init__(self, callback: Callable[[str], None]):
        """
        Initialize the base recognizer.
        
        Args:
            callback (Callable[[str], None]): Function to call with recognized text
        """
        self.callback = callback


    @abstractmethod
    def start(self) -> None:
        """
        Start continuous speech recognition.
        
        This method must be implemented by all recognizer classes.
        It should initialize and start the speech recognition process.
        
        Raises:
            NotImplementedError: If the child class doesn't implement this method
        """
        raise NotImplementedError("Recognizer must implement start method")
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop speech recognition completely.
        
        This method must be implemented by all recognizer classes.
        It should properly clean up and stop the speech recognition process.
        
        Raises:
            NotImplementedError: If the child class doesn't implement this method
        """
        raise NotImplementedError("Recognizer must implement stop method")
    
    @abstractmethod
    def _handle_result(self, evt: any) -> None:
        """
        Internal handler for speech recognition results.
        
        This method must be implemented by all recognizer classes.
        It should process recognition results and call the callback function
        with the recognized text. 
        
        Args:
            evt: Recognition event from the specific speech service
                  (type varies by implementation)
        
        Raises:
            NotImplementedError: If the child class doesn't implement this method
        """
        raise NotImplementedError("Recognizer must implement _handle_result method")
