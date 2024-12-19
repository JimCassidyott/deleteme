"""
Speech recognition implementations package.

This package contains different implementations of speech recognition services.
Currently supported:
- Azure Speech Services
"""

from .base_recognizer import BaseRecognizer
from .azure_recognizer import AzureRecognizer

__all__ = ['BaseRecognizer', 'AzureRecognizer']
