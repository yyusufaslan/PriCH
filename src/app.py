import tkinter as tk
import platform
from src.ui.main_window import MainWindow
from src.db.initialize import initialize_database
from src.services.clipboard_service import ClipboardService
from src.services.config_service import ConfigService

class PriCHApp:
    def __init__(self):
        # Initialize database on first run
        initialize_database()

        # Create config and load from database
        self.config = ConfigService()
        self.config.load_config_from_database() # Load config from database
        self.config.fetch_and_save_installed_apps() # Fetch and save installed apps
        
        # Create main window
        self.root = tk.Tk()
        self.root.title('PriCH - Clipboard Manager')
        self.root.geometry("1000x600")
        
        # Create history service
        self.clipboard_service = ClipboardService(self.config, None)
        
        # Create main window with history service
        self.main_window = MainWindow(self.root, self.clipboard_service)
        
        # Set the GUI reference in history service
        self.clipboard_service.gui = self.main_window.get_gui()
        
        # Start clipboard monitoring
        self.clipboard_service.start_monitor()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            # Cleanup
            self.clipboard_service.stop_monitor() 