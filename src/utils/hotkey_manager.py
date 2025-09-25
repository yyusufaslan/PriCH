import threading
import platform
from pynput import keyboard
from pynput.keyboard import Key, Listener

class HotkeyManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.listener = None
        self.running = False
        self.os_name = platform.system().lower()
        
        # Define hotkey combinations for different platforms
        if self.os_name == "darwin":  # macOS
            self.hotkey_combo = [Key.cmd, Key.space]  # Cmd+Space
        elif self.os_name == "windows":
            self.hotkey_combo = [Key.ctrl, Key.alt, Key.space]  # Ctrl+Alt+Space
        else:  # Linux
            self.hotkey_combo = [Key.ctrl, Key.alt, Key.space]  # Ctrl+Alt+Space
        
        # Track currently pressed keys
        self.pressed_keys = set()
        
    def start(self):
        """Start the hotkey listener"""
        if not self.running:
            self.running = True
            self.listener = Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
    
    def stop(self):
        """Stop the hotkey listener"""
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def _on_press(self, key):
        """Handle key press events"""
        try:
            # Add the key to pressed keys set
            self.pressed_keys.add(key)
            
            # Check if the hotkey combination is pressed
            if self._is_hotkey_pressed():
                self._trigger_hotkey()
                
        except AttributeError:
            # Handle special keys that might not have a char attribute
            pass
    
    def _on_release(self, key):
        """Handle key release events"""
        try:
            # Remove the key from pressed keys set
            self.pressed_keys.discard(key)
            
        except AttributeError:
            # Handle special keys that might not have a char attribute
            pass
    
    def _is_hotkey_pressed(self):
        """Check if the hotkey combination is currently pressed"""
        return all(key in self.pressed_keys for key in self.hotkey_combo)
    
    def _trigger_hotkey(self):
        """Trigger the hotkey action"""
        try:
            # Toggle window visibility
            if hasattr(self.main_window, 'is_window_hidden'):
                if self.main_window.is_window_hidden:
                    self.main_window.show_window()
                else:
                    self.main_window.hide_window()
            else:
                # Fallback: just show the window
                self.main_window.show_window()
        except Exception as e:
            print(f"Error triggering hotkey: {e}")
    
    def is_running(self):
        """Check if the hotkey manager is running"""
        return self.running
