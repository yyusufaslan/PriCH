import tkinter as tk
from src.ui.history_page import HistoryPage
from src.ui.settings_page import SettingsPage

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def is_running(self):
        return self.running
    
    def on_closing(self):
        self.running = False
        self.root.destroy()

class MainWindow:
    def __init__(self, root, clipboard_service):
        self.root = root
        self.gui = SimpleGUI(root)
        self.clipboard_service = clipboard_service
        
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.history_page = HistoryPage(self.frame, clipboard_service)
        self.settings_page = SettingsPage(self.frame, clipboard_service.config)
        
        # Create menu
        self.create_menu()
        
        # Show history page by default
        self.show_history_page()

    def create_menu(self):
        """Create the main menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="History", command=self.show_history_page)
        file_menu.add_command(label="Settings", command=self.show_settings_page)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_history_page(self):
        """Show the history page"""
        self.settings_page.hide()
        self.history_page.show()

    def show_settings_page(self):
        """Show the settings page"""
        self.history_page.hide()
        self.settings_page.show()

    def show_about(self):
        """Show about dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("About", "PriCH - Clipboard Manager\nVersion 1.0\n\nA secure clipboard management application with text masking capabilities.")

    def get_gui(self):
        return self.gui 