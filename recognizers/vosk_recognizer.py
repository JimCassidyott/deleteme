"""
Vosk Speech Recognition Implementation.

This module provides a wrapper around the Vosk speech recognition library,
which offers offline speech recognition capabilities.

Note:
    Requires the vosk package and appropriate language models to be installed locally.
"""

import json
import os
import queue
import sounddevice as sd
from typing import Callable, Optional
from vosk import Model, KaldiRecognizer
from .base_recognizer import BaseRecognizer

class VoskRecognizer(BaseRecognizer):
    """
    A wrapper class for Vosk Speech Recognition.
    
    This class implements the BaseRecognizer interface using Vosk,
    providing offline speech recognition capabilities.
    """
    
    def __init__(self, callback: Callable[[str], None], model_path: str = None):
        """
        Initialize the Vosk Speech Recognizer.
        
        Args:
            callback (Callable[[str], None]): Function to call with recognized text
            model_path (str, optional): Path to Vosk model directory. If None, uses default path
        """
        super().__init__(callback)
        
        # Set default model path if none provided
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    "llms", "vosk-model-en-us-0.22")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at: {model_path}")
            
        # Initialize Vosk components
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        
        # Audio stream configuration
        self.audio_queue = queue.Queue()
        self.device_info = sd.query_devices(None, 'input')
        self.samplerate = int(self.device_info['default_samplerate'])
        
        # Stream state
        self.stream: Optional[sd.InputStream] = None
        self._running = False
    
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream to process incoming audio data."""
        if status:
            print(status)
        self.audio_queue.put(bytes(indata))
    
    def start(self) -> None:
        """Start continuous speech recognition."""
        if self._running:
            return
            
        self._running = True
        self.stream = sd.InputStream(
            callback=self.audio_callback,
            channels=1,
            samplerate=self.samplerate,
            blocksize=8000,
            dtype='int16'
        )
        self.stream.start()
        
        while self._running:
            try:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    self._handle_result(result)
            except Exception as e:
                print(f"Error processing audio: {e}")
                continue
    
    def stop(self) -> None:
        """Stop speech recognition completely."""
        self._running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        # Process any remaining audio in the buffer
        result = json.loads(self.recognizer.FinalResult())
        self._handle_result(result)
    
    def _handle_result(self, result: dict) -> None:
        """
        Internal handler for speech recognition results.
        
        Args:
            result (dict): Recognition result from Vosk
        """
        if 'text' in result and result['text'].strip():
            self.callback(result['text'])
