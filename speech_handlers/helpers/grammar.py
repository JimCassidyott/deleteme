"""
Grammar helper functions for processing text and speech.
"""

def is_indefinite_article(word):
    """
    Check if a word is an indefinite article ('a' or 'an').
    
    Args:
        word (str): The word to check
        
    Returns:
        bool: True if the word is an indefinite article, False otherwise
    """
    return word.lower() in {'a', 'an'}