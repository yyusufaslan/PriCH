import tkinter as tk
from src.ui.history_page import HistoryPage
from src.ui.settings_page import SettingsPage
from src.utils.hotkey_manager import HotkeyManager

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
        self.is_window_hidden = False  # Track window state
        # Get screen dimensions
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        self.window_height = self.height // 3

        # Configure root window to take 1/3 of screen height and full width
        #self.root.title("PriCH - Clipboard Manager")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{self.width}x{self.window_height}+0+{self.height - self.window_height}")
        self.root.resizable(False, False)  # Allow horizontal resize, prevent vertical resize
        
        # Bind focus events with better handling
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.bind("<FocusIn>", self.on_focus_in)
        
        # Make window borderless for a modern look
        #self.root.overrideredirect(True)
        
        # Create main container - entire window for pages
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Initialize both pages
        self.history_page = HistoryPage(self.main_container, clipboard_service, self)
        self.settings_page = SettingsPage(self.main_container, self.clipboard_service.config, self)
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager(self)
        
        # Create menu
        #self.create_menu()
        
        # Show history page by default
        self.show_history_page()
        
        # Start hotkey listener
        self.hotkey_manager.start()


    # Geliştirilmiş on_focus_out metodu
    def on_focus_out(self, event):
        # Pencere gizli değilse, gizleme işlemini 100ms sonra yap
        # Bu, pencere içi olayların gizlemeyi iptal etmesine olanak tanır.
        if not self.is_window_hidden:
            self.root.after(100, self.check_focus_and_hide)

    def check_focus_and_hide(self):
        # Eğer pencere hala aktif olarak odaklanmamışsa, gizle
        if not self.root.focus_get():
            self.root.withdraw()
            self.is_window_hidden = True

    # Fokus alındığında maximize
    def on_focus_in(self, event):
        try:
            # Only show if currently hidden
            if self.is_window_hidden:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                self.is_window_hidden = False
        except Exception as e:
            print(f"Error showing window: {e}")

    def is_child_of_root(self, widget):
        """Check if a widget is a child of our root window"""
        try:
            current = widget
            while current:
                if current == self.root:
                    return True
                current = current.master
            return False
        except:
            return False

    def show_window(self):
        """Manually show the window"""
        try:
            if self.is_window_hidden:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                self.is_window_hidden = False
        except Exception as e:
            print(f"Error showing window: {e}")

    def hide_window(self):
        """Manually hide the window"""
        try:
            if not self.is_window_hidden:
                self.root.withdraw()
                self.is_window_hidden = True
        except Exception as e:
            print(f"Error hiding window: {e}")

    def create_menu(self):
        """Create the main menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
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
        """Show the settings page in the same window"""
        self.history_page.hide()
        self.settings_page.show()

    def show_about(self):
        """Show about dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("About", "PriCH - Clipboard Manager\nVersion 1.0\n\nA secure clipboard management application with text masking capabilities.")

    def get_gui(self):
        return self.gui
        
    def cleanup(self):
        """Cleanup resources before exit"""
        if hasattr(self, 'hotkey_manager'):
            self.hotkey_manager.stop() 