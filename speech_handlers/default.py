"""
Default speech handler implementation.
"""

from typing import List
from .base import BaseSpeechHandler, ListeningState
import json
import os
import subprocess
import shutil
import winreg
from enum import Enum
from typing import Optional
import pyautogui

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
        
        # Common Windows applications and their executables
        self.common_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'paint': 'mspaint.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'terminal': 'wt.exe',
            'task manager': 'taskmgr.exe',
            'control panel': 'control.exe',
            'obsidian': r'C:\Users\jimca\AppData\Local\Programs\Obsidian\Obsidian.exe',
            'windsurf': r'C:\Users\jimca\AppData\Local\Programs\windsurf\Windsurf.exe',

        }
    
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
    
    def find_in_path(self, app_name: str) -> Optional[str]:
        """Find an executable in the system PATH."""
        # Try with and without .exe extension
        path = shutil.which(app_name) or shutil.which(f"{app_name}.exe")
        return path

    def find_in_registry(self, app_name: str) -> Optional[str]:
        """Find application path from Windows Registry."""
        try:
            # Try common registry locations
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
            ]

            for hkey, reg_path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, f"{reg_path}\\{app_name}.exe") as key:
                        path, _ = winreg.QueryValueEx(key, "")
                        if os.path.exists(path):
                            return path
                except WindowsError:
                    continue
        except Exception:
            pass
        return None

    def launch_application(self, app_name: str) -> bool:
        """
        Attempt to launch an application by name.
        
        Args:
            app_name: The name of the application to launch
            
        Returns:
            bool: True if launch successful, False otherwise
        """
        app_name = app_name.lower()
        
        # If it's in our common apps list, use that name
        exe_name = self.common_apps.get(app_name, app_name)
        
        # First, try finding it in the PATH
        path = self.find_in_path(exe_name)
        if path:
            try:
                subprocess.Popen([path])
                print(f"Launched {app_name}")
                return True
            except (FileNotFoundError, PermissionError):
                pass

        # Next, try finding it in the registry
        path = self.find_in_registry(exe_name)
        if path:
            try:
                subprocess.Popen([path])
                print(f"Launched {app_name}")
                return True
            except (FileNotFoundError, PermissionError):
                pass

        # Finally, try searching common installation directories
        program_dirs = [
            os.environ.get('PROGRAMFILES', 'C:/Program Files'),
            os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)'),
            os.environ.get('LOCALAPPDATA', ''),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
            os.environ.get('APPDATA', '')
        ]

        for directory in program_dirs:
            if not directory or not os.path.exists(directory):
                continue

            try:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.lower() == f"{exe_name}":
                            try:
                                full_path = os.path.join(root, file)
                                subprocess.Popen([full_path])
                                print(f"Launched {app_name}")
                                return True
                            except (FileNotFoundError, PermissionError):
                                continue
            except (PermissionError, OSError):
                continue

        print(f"Could not find application: {app_name}")
        return False

    def close_application(self, app_name: str) -> None:
        """
        Close a specific application by name.
        
        Args:
            app_name (str): Name of the application to close
        """
        # Get the executable name from common apps if it exists
        if app_name in self.common_apps:
            exe_name = os.path.basename(self.common_apps[app_name])
        else:
            exe_name = app_name + '.exe'
            
        try:
            # Use taskkill to close the application
            subprocess.run(['taskkill', '/IM', exe_name, '/F'], 
                         capture_output=True, 
                         check=True)
        except subprocess.CalledProcessError:
            print(f"Could not close {app_name}")
            
    def handle_speech(self, text: str) -> str:
        """
        Handle incoming speech text by processing and executing the commands.
        
        Args:
            text (str): The recognized speech text to process
            
        Returns:
            str: The processed text, possibly modified by command processing
        """
        words = text.lower().split()
        
        # Check if this is a command
        if len(words) >= 2 and words[0] in ["leah", "lea", "leeah", "leia", "laya", "layah", "leja", "lejah"]:
            command = words[1]
            
            # Handle stop command
            if command == "stop":
                self.state = ListeningState.STOPPED
                return ""
                
            # Handle pause command
            elif command == "pause":
                self.state = ListeningState.PAUSED
                return ""
                
            # Handle resume command
            elif command == "resume":
                self.state = ListeningState.LISTENING
                return ""
                
            # Handle launch command
            elif command == "launch" and len(words) > 2:
                app_name = ' '.join(words[2:]).lower()
                self.launch_application(app_name)
                return ""
                
            # Handle close command
            elif command == "close":
                if len(words) > 2:
                    # Close specific application
                    app_name = ' '.join(words[2:]).lower()
                    self.close_application(app_name)
                else:
                    # Close active window with Alt+F4
                    pyautogui.hotkey('alt', 'f4')
                return ""

            # Handle press return command
            elif command == "press" and len(words) > 2 and words[2] == "return":
                pyautogui.press('enter')
                return ""
                
        # Pass the text down the handler chain
        return self.handle_chain(text)

    def handle_chain(self, text: str) -> str:
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
        elif "leah launch " in text_lower:
            app_name = text_lower[12:].strip()  # Get everything after "leah launch "
            if app_name:
                self.launch_application(app_name)
                return text
        else:
            # Type recognized text if we're in listening state
            if self.state == ListeningState.LISTENING:
                try:
                    if len(self._handler_chain) > 0:
                        return self._handler_chain[0].handle_speech(text)
                except Exception as e:
                    print(f"Error processing text: {e}")  # Debug print for errors
        
        return text
