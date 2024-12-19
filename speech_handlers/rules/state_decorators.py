"""
Decorators for enforcing speech handler states.
"""

from ..base import ListeningState

def leia_must_be_listening(state: ListeningState):
    """Decorator to ensure a speech handler is in the required state before processing.
    
    Args:
        required_state (ListeningState): The state that must be active for the function to execute
        
    Returns:
        The decorated function that checks the state before execution
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            print(f"Current state: {self.state}")
            if self.state != state:
                return args[0] if args else None
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
