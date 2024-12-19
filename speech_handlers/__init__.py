"""
Speech handlers module for processing recognized speech text.
"""

# from .root import RootSpeechHandler
from .default import DefaultSpeechHandler
from .dictation import DictationSpeechHandler

__all__ = ['DefaultSpeechHandler', 'DictationSpeechHandler']
