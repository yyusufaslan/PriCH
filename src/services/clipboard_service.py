import threading
import time
import pyperclip
from src.services.text_processor import TextProcessor
from src.db.clipboard_repository import ClipboardRepository
from src.utils.platform_utils import PlatformUtils
from src.services.checkers.allowed_app_checker import AllowedAppChecker

class ClipboardState:
    def __init__(self):
        self.download_requested = False
        self.model_to_download = None
        self.download_success = False
        self.download_completed = False
        self.last_given_text = ""
        self.last_copied_process = ""
        self.last_original_text = ""
        self.last_masked_text = ""
        self.last_mask_mapping = []
        self.was_modified_by_app = False
        self.state_mutex = threading.Lock()
        self.download_cv = threading.Condition(self.state_mutex)

class ClipboardService:
    def __init__(self, config, gui):
        self.text_processor = TextProcessor(config)
        self.db = ClipboardRepository()
        self.state = ClipboardState()
        self.config = config
        self.gui = gui
        self.running = True
        self.monitor_thread = None
        self.platform_utils = PlatformUtils()
        self.allowed_app_checker = AllowedAppChecker(config)
        
    def start_monitor(self):
        """Start the clipboard monitoring thread"""
        pyperclip.copy("")
        self.monitor_thread = threading.Thread(target=self.clipboard_monitor_thread, daemon=True)
        self.monitor_thread.start()
        print("Clipboard monitoring started")

    def clipboard_monitor_thread(self):
        """Main clipboard monitoring loop - runs every second"""
        state = self.state
        
        print("Clipboard monitor thread started")
        
        while self.running and (self.gui is None or self.gui.is_running()):
            try:
                # Read current clipboard content
                current_clipboard_text = pyperclip.paste()
                    
                # Get current active process and window
                active_process = self.platform_utils.get_active_process_name()
                active_window = self.platform_utils.get_active_window_title()
                
                # Check if clipboard text has changed (new copy operation)
                if current_clipboard_text != state.last_given_text:
                    print(f"Clipboard changed: {current_clipboard_text[:50]}...")
                    print(f"Active process: {active_process}")
                    print(f"Active window: {active_window}")
                    
                    # Save original text and process it
                    state.last_original_text = current_clipboard_text
                    state.last_copied_process = active_process
                    
                    # Process the clipboard text
                    self.process_clipboard_change(current_clipboard_text, active_process)
                else:
                    # Same text, check if we need to switch between original/processed based on app
                    self.process_clipboard_change_same_text(active_process, active_window)
                    
                # Wait 1 second before next check
                time.sleep(1)
                
            except Exception as e:
                import traceback
                print(f"Error in clipboard monitor: {e}")
                print(f"Error details: {traceback.format_exc()}")
                time.sleep(1)

    def process_clipboard_change(self, clipboard_text, active_process):
        """Process clipboard text when it changes (new copy operation)"""
        try:
            state = self.state
            
            # Check if masking is disabled
            if self.config.disable_masking:
                # Just save to database without processing
                self.text_processor.process_text(clipboard_text, state.last_mask_mapping, active_process)
                state.last_given_text = clipboard_text
                return
            
            # New text - check for unmasking
            if state.last_mask_mapping and not self.config.unMaskManual:
                match_count = 0
                for mapping in state.last_mask_mapping:
                    if mapping.get('maskedText') and mapping['maskedText'] in clipboard_text:
                        match_count += 1
                
                if state.last_mask_mapping:
                    match_ratio = match_count / len(state.last_mask_mapping)
                    if match_ratio >= 0.7:
                        # Unmask the text
                        clipboard_text = self.text_processor.replace_values_with_keys(
                            clipboard_text, state.last_original_text, state.last_mask_mapping)
            
            # Process the text (masking will be implemented later)
            processed_text = self.text_processor.process_text(clipboard_text, state.last_mask_mapping, active_process)
            
            # Save processed text but keep original text in clipboard for same app
            state.last_masked_text = processed_text
            state.last_given_text = clipboard_text  # Keep original text in clipboard initially
            
            print(f"Processed clipboard: {processed_text[:50]}...")
            
        except Exception as e:
            import traceback
            print(f"Error in process_clipboard_change: {e}")
            print(f"Error details: {traceback.format_exc()}")
            print(f"Clipboard text: {clipboard_text[:100]}...")
            print(f"Active process: {active_process}")

    def process_clipboard_change_same_text(self, active_process, active_window):
        """Process clipboard text when it is the same as before (pasting in different app)"""
        try:
            state = self.state
            
            # If masking is disabled, do nothing
            if self.config.disable_masking:
                return
            
            # Check if this is the same process as where we copied from
            if active_process == state.last_copied_process:
                # Same app - show original text
                if state.last_given_text != state.last_original_text:
                    pyperclip.copy(state.last_original_text)
                    state.last_given_text = state.last_original_text
                    print(f"Same app - showing original text")
            else:
                # Different app - check if trusted
                is_trusted = self.allowed_app_checker.is_trusted_app(active_window)
                if self.config.debugMode:
                    print(f"Different app - Is trusted: {is_trusted}")
                
                if is_trusted:
                    # Trusted app - show original text
                    if state.last_given_text != state.last_original_text:
                        pyperclip.copy(state.last_original_text)
                        state.last_given_text = state.last_original_text
                        if self.config.debugMode:
                            print(f"Trusted app - showing original text")
                else:
                    # Untrusted app - show processed/masked text
                    if state.last_given_text != state.last_masked_text:
                        pyperclip.copy(state.last_masked_text)
                        state.last_given_text = state.last_masked_text
                        if self.config.debugMode:
                            print(f"Untrusted app - showing masked text")
                        
        except Exception as e:
            import traceback
            print(f"Error in process_clipboard_change_same_text: {e}")
            print(f"Error details: {traceback.format_exc()}")
            print(f"Active process: {active_process}")
            print(f"Active window: {active_window}")

    def stop_monitor(self):
        """Stop the clipboard monitoring thread"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join()
        print("Clipboard monitoring stopped")

    def get_history(self, limit=100):
        """Get clipboard history from database with mask mappings"""
        return self.db.get_history_with_mappings(limit=limit) 