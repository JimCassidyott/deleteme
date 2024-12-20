"""
This is Leia's ear. It will listen to you and and manage the agent state. Leia was 
designed to host multiple agents that can perform multiple tasks. 

Vision: If all goes well with the design it should be extensible to any number of agents 
written in multiple programming languages that use gRPC to communicate with each other.

This module provides continuous speech recognition functionality using
various speech recognition backends. It handles the initialization and
management of the speech recognition service while providing a simple
interface for handling recognized speech.
"""

import threading
from datetime import datetime
from enum import Enum
import tkinter as tk
from tkinter import ttk
import time
import os
from PIL import Image, ImageTk
from recognizers import AzureRecognizer
from speech_handlers import DefaultSpeechHandler, DictationSpeechHandler

class ListeningState(Enum):
    """Enumeration of possible listening states for the speech recognition system."""
    LISTENING = "listening"  # Actively listening and outputting recognized speech
    PAUSED = "paused"       # Still listening but not outputting recognized speech

class SplashScreen:
    def __init__(self, controller):
        """Initialize the splash/control window."""
        self.controller = controller
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size and position - made wider to accommodate image
        window_width = 600
        window_height = 300
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Set background color to custom indigo (#001b38)
        self.root.configure(bg='#001b38')
        
        # Create main frame with custom indigo background
        main_frame = ttk.Frame(self.root, style='CustomIndigo.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Configure style for custom indigo background and white text
        style = ttk.Style()
        style.configure('CustomIndigo.TFrame', background='#001b38')
        style.configure('CustomIndigo.TLabel', background='#001b38', foreground='white')
        style.configure('Status.TLabel', background='#001b38', foreground='#FFD700', font=('Helvetica', 14))
        
        # Configure button style
        style.configure('Control.TButton', 
                      background='#708090',  # Slate grey
                      foreground='white',
                      padding=(20, 10),  # Increased horizontal padding
                      font=('Helvetica', 10, 'bold'),  # Bold font for better visibility
                      anchor='center',  # Center the text
                      width=10)  # Fixed width for consistent button size
        
        # Configure button layout to ensure text centering
        style.layout('Control.TButton', [
            ('Button.padding', {'children': [
                ('Button.label', {'sticky': 'nswe'})  # Make label fill the button
            ], 'sticky': 'nswe'})
        ])
        
        # Create left frame for image and right frame for text
        left_frame = ttk.Frame(main_frame, style='CustomIndigo.TFrame')
        left_frame.pack(side='left', padx=20, pady=20)
        
        right_frame = ttk.Frame(main_frame, style='CustomIndigo.TFrame')
        right_frame.pack(side='right', padx=20, pady=20, fill='both', expand=True)
        
        # Load and display the image
        image_path = os.path.join(os.path.dirname(__file__), 'files', 'images', 'leia.jpg')
        img = Image.open(image_path)
        # Resize image while maintaining aspect ratio - 20% bigger
        target_height = 240  # Increased from 200 to 240 (20% increase)
        aspect_ratio = img.width / img.height
        target_width = int(target_height * aspect_ratio)
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # Create label for image
        image_label = ttk.Label(left_frame, image=photo, style='CustomIndigo.TLabel')
        image_label.image = photo  # Keep a reference to prevent garbage collection
        image_label.pack(side='left')
        
        # Add title to right frame
        title_label = ttk.Label(right_frame, text="Leia-0.4.0", 
                               font=('Helvetica', 24, 'bold'),
                               style='CustomIndigo.TLabel')
        title_label.pack(pady=20)
        
        # Add subtitle to right frame
        subtitle_label = ttk.Label(right_frame, text="Language Enhanced Intelligent Agent", 
                                 font=('Helvetica', 12),
                                 style='CustomIndigo.TLabel')
        subtitle_label.pack()
        
        # Add status label
        self.status_label = ttk.Label(right_frame, text="Status: Initializing...", 
                                    style='Status.TLabel')
        self.status_label.pack(pady=20)
        
        # Add control buttons
        button_frame = ttk.Frame(right_frame, style='CustomIndigo.TFrame')
        button_frame.pack(pady=20)
        
        self.toggle_button = ttk.Button(button_frame, 
                                      text="Pause", 
                                      style='Control.TButton',
                                      command=self.toggle_state)
        self.toggle_button.pack(side='left', padx=10)
        
        self.stop_button = ttk.Button(button_frame, 
                                    text="Stop", 
                                    style='Control.TButton',
                                    command=self.stop_app)
        self.stop_button.pack(side='left', padx=10)
        
        # Author info in right frame
        author_label = ttk.Label(right_frame, text="Created by Jim Cassidy",
                               font=('Helvetica', 10),
                               style='CustomIndigo.TLabel')
        author_label.pack(side='bottom', pady=5)
        
        # Copyright info in right frame
        copyright_label = ttk.Label(right_frame, text=" 2024",
                                  font=('Helvetica', 10),
                                  style='CustomIndigo.TLabel')
        copyright_label.pack(side='bottom', pady=5)
        
        # Make entire window draggable
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.do_move)
        
        # Make all frames draggable
        main_frame.bind('<Button-1>', self.start_move)
        main_frame.bind('<B1-Motion>', self.do_move)
        left_frame.bind('<Button-1>', self.start_move)
        left_frame.bind('<B1-Motion>', self.do_move)
        right_frame.bind('<Button-1>', self.start_move)
        right_frame.bind('<B1-Motion>', self.do_move)
        
        # Make labels draggable
        image_label.bind('<Button-1>', self.start_move)
        image_label.bind('<B1-Motion>', self.do_move)
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.do_move)
        subtitle_label.bind('<Button-1>', self.start_move)
        subtitle_label.bind('<B1-Motion>', self.do_move)
        self.status_label.bind('<Button-1>', self.start_move)
        self.status_label.bind('<B1-Motion>', self.do_move)
        
        # Exclude buttons from dragging to maintain click functionality
        button_frame.bind('<Button-1>', lambda e: e.widget.focus_set())
        self.toggle_button.bind('<Button-1>', lambda e: e.widget.focus_set())
        self.stop_button.bind('<Button-1>', lambda e: e.widget.focus_set())
        
        # Store initial click position
        self.click_x = 0
        self.click_y = 0
        
        # Update status periodically
        self.root.after(100, self.update_status)
    
    def start_move(self, event):
        """Start window drag."""
        # Store the initial click position relative to the window
        self.click_x = event.x_root - self.root.winfo_x()
        self.click_y = event.y_root - self.root.winfo_y()

    def do_move(self, event):
        """Handle window drag."""
        # Calculate new position
        new_x = event.x_root - self.click_x
        new_y = event.y_root - self.click_y
        
        # Move window without bounds checking
        self.root.geometry(f"+{new_x}+{new_y}")
    
    def toggle_state(self):
        """Toggle between pause and resume."""
        if self.controller.state == ListeningState.LISTENING:
            self.controller.pause()
            self.toggle_button.configure(text="Resume")
        else:
            self.controller.resume()
            self.toggle_button.configure(text="Pause")
    
    def stop_app(self):
        """Stop the application."""
        self.controller.stop()
        self.root.quit()
    
    def update_status(self):
        """Update the status display."""
        status_text = "Status: "
        if self.controller.state == ListeningState.LISTENING:
            status_text += "Listening"
        else:
            status_text += "Paused"
        self.status_label.configure(text=status_text)
        self.root.after(100, self.update_status)
    
    def update_button_text(self):
        """Update the toggle button text based on current state."""
        if self.controller.state == ListeningState.LISTENING:
            self.toggle_button.configure(text="Pause")
        else:
            self.toggle_button.configure(text="Resume")

    def show(self):
        """Show the control window."""
        self.root.mainloop()

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
        
        # Create and show the control window
        self.window = SplashScreen(self)
    
    def handle_speech(self, text: str):
        """
        Route speech text to the handler.
        
        Args:
            text (str): The recognized speech text to process
        """
        # Get timestamp for logging
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Print the recognized text with timestamp
        print(f"[{timestamp}] {text}")
        
        # Use lowercase only for command checking
        command_text = text.lower().strip()
        
        # Check for control commands
        if command_text == "leah pause" and self.state == ListeningState.LISTENING:
            self.pause()
            self.window.update_button_text()
        elif command_text == "leah resume" and self.state == ListeningState.PAUSED:
            self.resume()
            self.window.update_button_text()
        elif command_text == "leah stop":
            self.stop()
            return
        
        # Pass the text to the handler for further processing and output
        if self.state == ListeningState.LISTENING:
            self.handler.handle_speech(text)
    
    def start(self):
        """Start the speech recognition system."""
        # Start recognition in a separate thread
        recognition_thread = threading.Thread(target=self.run_recognition)
        recognition_thread.daemon = True
        recognition_thread.start()
        
        # Show the control window (this will block until window is closed)
        self.window.show()
    
    def run_recognition(self):
        """Run the speech recognition loop."""
        try:
            self.recognizer.start()
            self.done.wait()
        finally:
            self.recognizer.stop()
    
    def stop(self):
        """Stop speech recognition and signal the system to shut down."""
        self.done.set()
    
    def pause(self):
        """
        Pause speech output.
        
        Recognition continues but recognized speech is not printed.
        Voice commands are still processed.
        """
        if self.state == ListeningState.LISTENING:
            self.state = ListeningState.PAUSED
            self.recognizer.set_paused(True)
    
    def resume(self):
        """Resume speech output after being paused."""
        if self.state == ListeningState.PAUSED:
            self.state = ListeningState.LISTENING
            self.recognizer.set_paused(False)

def main():
    """Main entry point for the speech recognition system."""
    controller = SpeechController()
    controller.start()

if __name__ == "__main__":
    main()
