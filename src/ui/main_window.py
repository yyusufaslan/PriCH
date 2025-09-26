import tkinter as tk
import customtkinter as ctk
import time
from src.ui.history_page import HistoryPage
from src.ui.settings_page import SettingsPage
from src.utils.hotkey_manager import HotkeyManager

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.main_window = None
    
    def is_running(self):
        return self.running
    
    def on_closing(self):
        self.running = False
        self.root.destroy()

    def set_main_window(self, main_window):
        """Register the MainWindow so central refresh methods can access pages"""
        self.main_window = main_window

    def refresh_history(self):
        """Central method to refresh the history UI safely on the Tk thread"""
        try:
            if self.main_window and hasattr(self.main_window, 'history_page'):
                self.root.after(0, self.main_window.history_page.refresh_history)
        except Exception as e:
            print(f"Error refreshing history UI: {e}")

    def refresh_settings(self):
        """Central method to refresh the settings UI safely on the Tk thread"""
        try:
            if self.main_window and hasattr(self.main_window, 'settings_page'):
                # If settings has any dynamic reload method, call it here in future
                pass
        except Exception as e:
            print(f"Error refreshing settings UI: {e}")

    def refresh_visible_page(self):
        """Optionally refresh whichever page is currently visible"""
        try:
            if not self.main_window:
                return
            # Determine which frame is packed
            if self.main_window.history_page and self.main_window.history_page.frame.winfo_ismapped():
                self.refresh_history()
            elif self.main_window.settings_page and self.main_window.settings_page.frame.winfo_ismapped():
                self.refresh_settings()
        except Exception as e:
            print(f"Error refreshing visible page: {e}")

class MainWindow:
    def __init__(self, root, clipboard_service):
        self.root = root
        self.gui = SimpleGUI(root)
        self.clipboard_service = clipboard_service
        self.is_window_hidden = False  # Track window state
        self._drag_start_y = None
        self._visible_frame = None  # (x, y, w, h) of visible area
        self._suppress_hide_until = 0.0  # monotonic deadline to ignore auto-hide
        self._hide_after_id = None
        
        # Configure customtkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Get screen dimensions
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        self.window_height = self.height // 2

        # Configure root window to take 1/3 of screen height and full width
        #self.root.title("PriCH - Clipboard Manager")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        # On macOS, set a non-activating floating style to avoid space switching
        self._apply_macos_window_style()
        # Compute visible frame (macOS: area above Dock)
        self._compute_visible_frame()
        x0, y0, w0, h0 = self._visible_frame if self._visible_frame else (0, 0, self.width, self.height)
        # Place window so it sits just above the Dock (bottom inset)
        y_initial = self._calc_initial_y()
        self.root.geometry(f"{w0}x{self.window_height}+{x0}+{y_initial}")
        # Fix size - user cannot resize
        self.root.resizable(False, False)
        
        # Bind focus events with better handling
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.bind("<FocusIn>", self.on_focus_in)
        
        # Create main container - entire window for pages
        self.main_container = ctk.CTkFrame(root, fg_color="#1a1a1a")
        self.main_container.pack(fill="both", expand=True)
        # Enable vertical drag across the screen
        self.main_container.bind("<ButtonPress-1>", self._on_drag_start)
        self.main_container.bind("<B1-Motion>", self._on_drag_motion)

        # Initialize both pages
        self.history_page = HistoryPage(self.main_container, clipboard_service, self)
        self.settings_page = SettingsPage(self.main_container, self.clipboard_service.config, self)
        # Register this main window on GUI facade for central refresh
        self.gui.set_main_window(self)
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager(self)
        
        # Show history page by default
        self.show_history_page()
        
        # Start hotkey listener
        self.hotkey_manager.start()
        # Ensure frontmost behavior on launch
        self._suppress_auto_hide(4)
        self._ensure_frontmost()

    def _apply_macos_window_style(self):
        try:
            import platform
            if platform.system() == "Darwin":
                # Make window floating and non-activating so it can appear over fullscreen without switching spaces
                try:
                    self.root.tk.call('::tk::unsupported::MacWindowStyle', 'style', self.root._w, 'floating', 'noActivates')
                except Exception:
                    pass
        except Exception:
            pass

    def _cancel_scheduled_hide(self):
        try:
            if self._hide_after_id is not None:
                self.root.after_cancel(self._hide_after_id)
        except Exception:
            pass
        finally:
            self._hide_after_id = None

    def _suppress_auto_hide(self, seconds: float):
        try:
            self._suppress_hide_until = time.monotonic() + max(0.0, seconds)
            self._cancel_scheduled_hide()
        except Exception:
            self._suppress_hide_until = 0.0

    def _auto_hide_suppressed(self) -> bool:
        try:
            return time.monotonic() < self._suppress_hide_until
        except Exception:
            return False

    def _compute_visible_frame(self):
        """Compute visible screen frame. On macOS, excludes Dock and menu bar."""
        try:
            import platform
            if platform.system() == "Darwin":
                try:
                    from AppKit import NSScreen
                    screen = NSScreen.mainScreen()
                    if screen is not None:
                        vf = screen.visibleFrame()
                        x = int(vf.origin.x)
                        y = int(vf.origin.y)
                        w = int(vf.size.width)
                        h = int(vf.size.height)
                        self._visible_frame = (x, y, w, h)
                        return
                except Exception:
                    pass
            if platform.system() == "Windows":
                self._visible_frame = (0, 0, self.width, self.height)
                return
            # Fallback: use full screen
            self._visible_frame = (0, 0, self.width, self.height)
        except Exception:
            self._visible_frame = (0, 0, self.width, self.height)

    def _calc_initial_y(self):
        """Calculate initial Y so window bottom aligns above Dock (if present)."""
        x0, y0, w0, h0 = self._visible_frame if self._visible_frame else (0, 0, self.width, self.height)
        # AppKit coordinates: y0 is bottom inset (Dock height). Tk y=0 is top.
        bottom_inset = y0
        return max(0, self.height - self.window_height - bottom_inset)

    def _clamp_y(self, y):
        """Clamp Y between top visible and just above Dock."""
        x0, y0, w0, h0 = self._visible_frame if self._visible_frame else (0, 0, self.width, self.height)
        top_inset = self.height - (y0 + h0)
        bottom_inset = y0
        min_y = max(0, top_inset)
        max_y = max(0, self.height - self.window_height - bottom_inset)
        if y < min_y:
            return min_y
        if y > max_y:
            return max_y
        return y

    def _on_drag_start(self, event):
        self._drag_start_y = event.y_root

    def _on_drag_motion(self, event):
        if self._drag_start_y is None:
            return
        try:
            # Parse current geometry
            geo = self.root.geometry()  # e.g., "1920x360+0+720"
            parts = geo.split("+")
            size = parts[0]
            x_curr = int(parts[1]) if len(parts) > 1 else 0
            y_curr = int(parts[2]) if len(parts) > 2 else 0
            delta_y = int(event.y_root - self._drag_start_y)
            new_y = self._clamp_y(y_curr + delta_y)
            x0, y0, w0, h0 = self._visible_frame if self._visible_frame else (0, 0, self.width, self.height)
            self.root.geometry(f"{w0}x{self.window_height}+{x0}+{new_y}")
            self._drag_start_y = event.y_root
        except Exception as e:
            print(f"Error dragging window: {e}")

    # Geliştirilmiş on_focus_out metodu
    def on_focus_out(self, event):
        # Pencere gizli değilse, gizleme işlemini 100ms sonra yap
        # Bu, pencere içi olayların gizlemeyi iptal etmesine olanak tanır.
        print("On focus out called")
        if self._auto_hide_suppressed():
            return
        if not self.is_window_hidden:
            self._cancel_scheduled_hide()
            self._hide_after_id = self.root.after(120, self.check_focus_and_hide)

    def check_focus_and_hide(self):
        # Eğer pencere hala aktif olarak odaklanmamışsa, gizle
        if self._auto_hide_suppressed():
            return
        self._hide_after_id = None
        if not self.root.focus_get():
            self.root.withdraw()
            self.is_window_hidden = True

    # Fokus alındığında maximize
    def on_focus_in(self, event):
        print("On focus in called")
        try:
            # Only show if currently hidden
            if self.is_window_hidden:
                self.root.deiconify()
                self.root.update_idletasks()
                self.root.lift()
                # Avoid forcing focus on macOS to prevent space switch
                try:
                    import platform
                    if platform.system() != "Darwin":
                        self.root.focus_force()
                except Exception:
                    pass
                self.is_window_hidden = False
            # Keep frontmost if possible
            self._suppress_auto_hide(4)
            self._ensure_frontmost()
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
                self.root.update_idletasks()
                self.root.lift()
                # Avoid forcing focus on macOS to prevent space switch
                try:
                    import platform
                    if platform.system() != "Darwin":
                        self.root.focus_force()
                except Exception:
                    pass
                self.is_window_hidden = False
            # Promote to front across spaces/fullscreen when possible
            self._suppress_auto_hide(4)
            self._ensure_frontmost()
        except Exception as e:
            print(f"Error showing window: {e}")

    def hide_window(self):
        """Manually hide the window"""
        try:
            if not self.is_window_hidden:
                self._cancel_scheduled_hide()
                self.root.withdraw()
                self.is_window_hidden = True
        except Exception as e:
            print(f"Error hiding window: {e}")

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

    def _ensure_frontmost(self):
        """On macOS, bring the window to front above fullscreen apps and on all spaces without switching spaces."""
        print("Ensure frontmost called")
        try:
            import platform
            print("Platform system: ", platform.system())
            if platform.system() != "Darwin":
                # Best effort on other OSes
                self.root.deiconify()
                self.root.attributes("-topmost", True)
                self.root.lift()
                print("App brought to front1")
                return
            try:
                from AppKit import NSApp, NSScreenSaverWindowLevel, NSWindowCollectionBehaviorCanJoinAllSpaces, NSWindowCollectionBehaviorFullScreenAuxiliary
                app = NSApp()
                # Do NOT activate the app to avoid space switch; just raise the window(s)
                for win in app.windows():
                    try:
                        if not win.isVisible():
                            continue
                        # Show on all spaces and allow over fullscreen
                        win.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces | NSWindowCollectionBehaviorFullScreenAuxiliary)
                        # Use a very high floating level so it appears as a popup overlay
                        win.setLevel_(NSScreenSaverWindowLevel)
                        win.orderFrontRegardless()
                    except Exception:
                        continue
                # Also ensure Tk window is up
                self.root.deiconify()
                self.root.attributes("-topmost", True)
                self.root.lift()
                print("App brought to front2")
            except Exception:
                # PyObjC not available or other failure; fallback to Tk behavior
                self.root.deiconify()
                self.root.attributes("-topmost", True)
                self.root.lift()
        except Exception:
            pass 