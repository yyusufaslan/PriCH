import tkinter as tk
from tkinter import messagebox
import datetime
import platform
import customtkinter as ctk

class HistoryPage:
    def __init__(self, parent, clipboard_service, main_window=None):
        self.frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        self.clipboard_service = clipboard_service
        self.main_window = main_window
        self.auto_refresh_enabled = False
        self.auto_refresh_id = None
        self.cards_frame = None
        self.canvas = None
        self.scrollbar = None
        self.category_canvas = None
        self.category_scrollbar = None
        
        # Configure customtkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.create_layout()
        self.refresh_history()
        self.start_auto_refresh()

    def create_layout(self):
        self.create_header()
        self.create_scrollable_content()
        
    def create_header(self):
        header_container = ctk.CTkFrame(self.frame, fg_color="#2d2d2d", height=55)
        header_container.pack(fill="x", padx=0, pady=0)
        header_container.pack_propagate(False)
        
        header_frame = ctk.CTkFrame(header_container, fg_color="#2d2d2d")
        header_frame.pack(fill="both", padx=10, pady=5)
        
        
        left_section = ctk.CTkFrame(header_frame, fg_color="#2d2d2d")
        left_section.pack(side="left", fill="y")
        
        disable_btn = ctk.CTkButton(
            left_section, 
            text="Disable Features", 
            command=self.disable_features,
            fg_color="#6c757d",
            hover_color="#5a6268",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            width=100,
            height=25
        )
        disable_btn.pack(side="left", padx=(0, 10))
        
        search_container = ctk.CTkFrame(header_frame, fg_color="#2d2d2d")
        search_container.pack(side="left", padx=(0, 15))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        
        search_entry = ctk.CTkEntry(
            search_container,
            textvariable=self.search_var,
            placeholder_text="Search in Original Text",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=250,
            height=20,
            fg_color="#404040",
            text_color="white",
            border_color="#404040"
        )
        search_entry.pack(padx=15, pady=5)
        
        categories_container = ctk.CTkFrame(header_frame, fg_color="#2d2d2d")
        categories_container.pack(side="left", fill="x", expand=True, padx=(0, 0))
        
        self.create_category_tags(categories_container)
        
        right_section = ctk.CTkFrame(header_frame, fg_color="#2d2d2d")
        right_section.pack(side="right", fill="y")
        
        menu_btn = ctk.CTkButton(
            right_section, 
            text="Menu", 
            command=self.show_menu,
            fg_color="#6c757d",
            hover_color="#5a6268",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            width=60,
            height=25
        )
        menu_btn.pack(side="right")

    def create_category_tags(self, parent):
        categories = [
            "ASCSAREWREV", "ASFASDCZXC2", "DFGFDGERERT", "FDSFSDFSDFS", 
            "GHFGHFGNBF", "HFGHFGHFGHF", "Java Codes", "SADASFDSVX", 
            "ZZZZXZCZX", "asdasdas", "dasdadasdas", "dasdascssS", 
            "ffffffffff", "faefd", "sadAASASDAS", "vvxcvsd"
        ]
        
        # Create a scrollable frame for categories
        self.category_canvas = ctk.CTkScrollableFrame(
            parent,
            fg_color="#2d2d2d",
            height=40,
            orientation="horizontal"
        )
        self.category_canvas.pack(side="left", fill="x", expand=True)
        
        for category in categories:
            tag_btn = ctk.CTkButton(
                self.category_canvas,
                text=category,
                font=ctk.CTkFont(family="Segoe UI", size=9),
                fg_color="#404040",
                hover_color="#4a90e2",
                text_color="white",
                width=100,
                height=25,
                command=lambda cat=category: self.on_category_click(cat)
            )
            tag_btn.pack(side="left", padx=(0, 3), pady=0)

    def create_scrollable_content(self):
        canvas_frame = ctk.CTkFrame(self.frame, fg_color="#1a1a1a")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # Create a scrollable frame for the cards
        self.cards_frame = ctk.CTkScrollableFrame(
            canvas_frame,
            fg_color="#1a1a1a",
            orientation="horizontal"
        )
        self.cards_frame.pack(fill="both", expand=True)

    def create_history_card(self, history_item, card_index):
        card_container = ctk.CTkFrame(self.cards_frame, fg_color="#2d2d2d", width=320, height=320)
        card_container.pack(side="left", padx=(0, 10), pady=0)
        card_container.pack_propagate(False)
        
        content_frame = ctk.CTkFrame(card_container, fg_color="#2d2d2d")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header frame
        header_frame = ctk.CTkFrame(content_frame, fg_color="#2d2d2d")
        header_frame.pack(fill="x", pady=(0, 5))
        
        timestamp = history_item.get('timestamp', 'Unknown')
        if isinstance(timestamp, str) and len(timestamp) > 15:
            timestamp = timestamp[:15] + "..."
        
        timestamp_label = ctk.CTkLabel(
            header_frame,
            text=timestamp,
            font=ctk.CTkFont(family="Segoe UI", size=9),
            fg_color="#2d2d2d",
            text_color="#b0b0b0"
        )
        timestamp_label.pack(side="left")

        source = history_item.get('sourceProcess', 'Unknown')
        if len(source) > 12:
            source = source[:12] + "..."
        
        source_label = ctk.CTkLabel(
            header_frame,
            text=source,
            font=ctk.CTkFont(family="Segoe UI", size=9),
            fg_color="#2d2d2d",
            text_color="#4a90e2"
        )
        source_label.pack(side="right")
        
        original_text = history_item.get('maskedText', '')
        
        # Text frame
        text_frame = ctk.CTkFrame(content_frame, fg_color="#2d2d2d")
        text_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        text_widget = ctk.CTkTextbox(
            text_frame,
            fg_color="#2d2d2d",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            width=300,
            height=200
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", original_text)
        text_widget.configure(state="disabled")
        
        # Footer frame
        footer_frame = ctk.CTkFrame(content_frame, fg_color="#2d2d2d")
        footer_frame.pack(fill="x")
        
        unmask_btn = ctk.CTkButton(
            footer_frame,
            text="⏎",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#2d2d2d",
            hover_color="#404040",
            text_color="white",
            width=30,
            height=25,
            command=lambda: self.unmask_text(history_item)
        )
        unmask_btn.pack(side="left", pady=3, padx=3)
        
        close_btn = ctk.CTkButton(
            footer_frame,
            text="✕",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#2d2d2d",
            hover_color="#dc3545",
            text_color="white",
            width=30,
            height=25,
            command=lambda: self.close_card(card_container, history_item)
        )
        close_btn.pack(side="right", pady=3, padx=3)
        
        # Bind click events to copy masked text
        card_container.bind("<Button-1>", lambda e, item=history_item: self.copy_to_clipboard(item.get('maskedText', '')))
        content_frame.bind("<Button-1>", lambda e, item=history_item: self.copy_to_clipboard(item.get('maskedText', '')))
        text_widget.bind("<Button-1>", lambda e, item=history_item: self.copy_to_clipboard(item.get('maskedText', '')))
        
        return card_container

    def close_card(self, card_container, history_item):
        card_container.destroy()

    def unmask_text(self, history_item):
        original_text = history_item.get('originalText', '')
        self.copy_to_clipboard(original_text)

    def on_search_change(self, *args):
        self.refresh_history()

    def on_category_click(self, category):
        print(f"Category clicked: {category}")

    def disable_features(self):
        messagebox.showinfo("Features", "Features disabled")

    def show_menu(self):
        # Create a custom menu using CTkFrame
        menu_window = ctk.CTkToplevel()
        menu_window.title("Menu")
        menu_window.geometry("200x250")
        menu_window.configure(fg_color="#2d2d2d")
        menu_window.attributes("-topmost", True)
        
        # Center the menu window
        menu_window.update_idletasks()
        x = (menu_window.winfo_screenwidth() // 2) - (200 // 2)
        y = (menu_window.winfo_screenheight() // 2) - (250 // 2)
        menu_window.geometry(f"200x250+{x}+{y}")
        
        menu_frame = ctk.CTkFrame(menu_window, fg_color="#2d2d2d")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Menu buttons
        refresh_btn = ctk.CTkButton(
            menu_frame,
            text="Refresh",
            command=lambda: [self.refresh_history(), menu_window.destroy()],
            fg_color="#4a90e2",
            hover_color="#357abd",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=180,
            height=35
        )
        refresh_btn.pack(pady=5)
        
        clear_btn = ctk.CTkButton(
            menu_frame,
            text="Clear All History",
            command=lambda: [self.clear_all_history(), menu_window.destroy()],
            fg_color="#dc3545",
            hover_color="#c82333",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=180,
            height=35
        )
        clear_btn.pack(pady=5)
        
        settings_btn = ctk.CTkButton(
            menu_frame,
            text="Settings",
            command=lambda: [self.open_settings(), menu_window.destroy()],
            fg_color="#6c757d",
            hover_color="#5a6268",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=180,
            height=35
        )
        settings_btn.pack(pady=5)
        
        exit_btn = ctk.CTkButton(
            menu_frame,
            text="Exit",
            command=lambda: [self.close_application(), menu_window.destroy()],
            fg_color="#dc3545",
            hover_color="#c82333",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=180,
            height=35
        )
        exit_btn.pack(pady=5)

    def clear_all_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all clipboard history?"):
            try:
                self.clipboard_service.db.clear_history()
                self.refresh_history()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {str(e)}")

    def open_settings(self):
        try:
            if self.main_window:
                self.main_window.show_settings_page()
            else:
                print("Warning: Main window reference not available")
                messagebox.showwarning("Settings", "Unable to open settings. Please try again.")
        except Exception as e:
            print(f"Error opening settings: {e}")
            messagebox.showerror("Error", f"Failed to open settings: {str(e)}")

    def close_application(self):
        try:
            root = self.frame.winfo_toplevel()
            root.quit()
        except Exception as e:
            print(f"Error closing application: {e}")

    def start_auto_refresh(self):
        if self.auto_refresh_enabled:
            self.refresh_history()
            self.auto_refresh_id = self.frame.after(15000, self.start_auto_refresh)

    def stop_auto_refresh(self):
        if self.auto_refresh_id:
            self.frame.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None

    def toggle_auto_refresh(self):
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        if self.auto_refresh_enabled:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def refresh_history(self):
        try:
            if not self.cards_frame:
                return
            
            # Clear existing cards
            for widget in self.cards_frame.winfo_children():
                widget.destroy()
            
            history = self.clipboard_service.get_history(limit=50)
            
            search_term = self.search_var.get().lower()
            if search_term and search_term != "search in original text":
                filtered_history = []
                for entry in history:
                    item_as_dict = entry if isinstance(entry, dict) else {
                        'originalText': entry[1] if len(entry) > 1 else '',
                        'maskedText': entry[2] if len(entry) > 2 else '',
                        'sourceProcess': entry[3] if len(entry) > 3 else '',
                    }
                    if any(search_term in str(value).lower() for value in item_as_dict.values()):
                        filtered_history.append(entry)
                history = filtered_history
            
            for i, entry in enumerate(history):
                if isinstance(entry, dict):
                    history_item = entry
                else:
                    history_item = {
                        'originalText': entry[1] if len(entry) > 1 else '',
                        'maskedText': entry[2] if len(entry) > 2 else '',
                        'sourceProcess': entry[3] if len(entry) > 3 else '',
                        'timestamp': entry[4] if len(entry) > 4 else '',
                        'createdAt': entry[5] if len(entry) > 5 else ''
                    }
                self.create_history_card(history_item, i)
            
        except Exception as e:
            print(f"Error refreshing history: {e}")

    def copy_to_clipboard(self, text):
        import pyperclip
        pyperclip.copy(text)

    def show(self):
        self.frame.pack(fill="both", expand=True)
        if not self.cards_frame:
            self.create_layout()
        if self.auto_refresh_enabled:
            self.start_auto_refresh()

    def hide(self):
        self.frame.pack_forget()
        self.stop_auto_refresh()