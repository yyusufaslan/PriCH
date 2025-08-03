import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class HistoryPage:
    def __init__(self, parent, clipboard_service, main_window=None):
        self.frame = tk.Frame(parent, bg="#1a1a1a")
        self.clipboard_service = clipboard_service
        self.main_window = main_window
        self.auto_refresh_enabled = True
        self.auto_refresh_id = None
        self.cards_frame = None
        self.canvas = None
        self.scrollbar = None
        self.category_canvas = None
        self.category_scrollbar = None
        
        self.create_layout()
        self.refresh_history()
        self.start_auto_refresh()

    def create_layout(self):
        self.create_header()
        self.create_scrollable_content()
        
    def create_header(self):
        header_container = tk.Frame(self.frame, bg="#2d2d2d", height=35)
        header_container.pack(fill=tk.X, padx=0, pady=0)
        header_container.pack_propagate(False)
        
        header_frame = tk.Frame(header_container, bg="#2d2d2d")
        header_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        left_section = tk.Frame(header_frame, bg="#2d2d2d")
        left_section.pack(side=tk.LEFT, fill=tk.Y)
        
        disable_btn = self.create_modern_button(left_section, "Disable Features", 
                                                command=self.disable_features, 
                                                bg="#6c757d", fg="white",
                                                font=("Segoe UI", 8))
        disable_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        search_container = tk.Frame(header_frame, bg="#2d2d2d")
        search_container.pack(side=tk.LEFT, padx=(0, 10))
        
        search_frame = tk.Frame(search_container, bg="#404040", relief=tk.FLAT, bd=0)
        search_frame.pack(padx=0, pady=0)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                font=("Segoe UI", 8), width=30, relief=tk.FLAT, 
                                bg="#404040", fg="white", insertbackground="white",
                                selectbackground="#4a90e2", selectforeground="white")
        search_entry.pack(padx=15, pady=5)
        search_entry.insert(0, "Search in Original Text")
        search_entry.bind("<FocusIn>", lambda e: self.on_search_focus_in(search_entry))
        search_entry.bind("<FocusOut>", lambda e: self.on_search_focus_out(search_entry))
        
        categories_container = tk.Frame(header_frame, bg="#2d2d2d")
        categories_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.create_category_tags(categories_container)
        
        right_section = tk.Frame(header_frame, bg="#2d2d2d")
        right_section.pack(side=tk.RIGHT, fill=tk.Y)
        
        menu_btn2 = self.create_modern_button(right_section, "Menu", 
                                              command=self.show_menu, 
                                              bg="#6c757d", fg="white",
                                              font=("Segoe UI", 10), width=5, height=1)
        menu_btn2.pack(side=tk.RIGHT)

    def create_modern_button(self, parent, text, command, bg="#4a90e2", fg="white", 
                            font=("Segoe UI", 10), width=None, height=None):
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, 
                        font=font, relief=tk.FLAT, bd=0, cursor="hand2",
                        width=width, height=height, padx=5, pady=3)
        
        def on_enter(e):
            btn.config(bg=self.lighten_color(bg, 20))
        
        def on_leave(e):
            btn.config(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def lighten_color(self, color, amount):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, c + amount) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def create_category_tags(self, parent):
        categories = [
            "ASCSAREWREV", "ASFASDCZXC2", "DFGFDGERERT", "FDSFSDFSDFS", 
            "GHFGHFGNBF", "HFGHFGHFGHF", "Java Codes", "SADASFDSVX", 
            "ZZZZXZCZX", "asdasdas", "dasdadasdas", "dasdascssS", 
            "ffffffffff", "faefd", "sadAASASDAS", "vvxcvsd"
        ]
        
        self.category_canvas = tk.Canvas(parent, bg="#2d2d2d", highlightthickness=0, height=40)
        self.category_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.category_canvas.xview)
        scrollable_frame = tk.Frame(self.category_canvas, bg="#2d2d2d")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.category_canvas.configure(scrollregion=self.category_canvas.bbox("all"))
        )
        
        self.category_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.category_canvas.configure(xscrollcommand=self.category_scrollbar.set)
        
        # Fare tekerleği ile yatay kaydırma olayını bağla
        self.category_canvas.bind("<MouseWheel>", self.on_category_mousewheel)
        scrollable_frame.bind("<MouseWheel>", self.on_category_mousewheel)
        
        for i, category in enumerate(categories):
            tag_btn = tk.Button(scrollable_frame, text=category, 
                                font=("Segoe UI", 9), bg="#404040", fg="white", 
                                relief=tk.FLAT, bd=0, cursor="hand2",
                                command=lambda cat=category: self.on_category_click(cat))
            tag_btn.pack(side=tk.LEFT, padx=(0, 8), pady=5)
            
            def on_tag_enter(e, btn=tag_btn):
                btn.config(bg="#4a90e2")
            
            def on_tag_leave(e, btn=tag_btn):
                btn.config(bg="#404040")
            
            tag_btn.bind("<Enter>", on_tag_enter)
            tag_btn.bind("<Leave>", on_tag_leave)
        
        self.category_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Scrollbar'ı gizle
        # self.category_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_scrollable_content(self):
        canvas_frame = tk.Frame(self.frame, bg="#1a1a1a")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        self.canvas = tk.Canvas(canvas_frame, bg="#1a1a1a", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.cards_frame = tk.Frame(self.canvas, bg="#1a1a1a")
        
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        self.cards_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Mouse tekerleği ile yatay kaydırma
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self.on_mousewheel)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        canvas_items = self.canvas.find_withtag("all")
        if canvas_items:
            # Kartların çerçevesi için dinamik genişlik gerekmez,
            # sadece scroll bölgesinin doğru ayarlandığından emin olmak yeterlidir.
            # Bu satır kaldırıldı.
            pass

    def on_mousewheel(self, event):
        if platform.system() == 'Windows':
            # Windows'ta event.delta 120 veya -120 gelir
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            # macOS ve Linux'ta event.delta daha küçük değerler olabilir
            self.canvas.xview_scroll(int(-1 * event.delta), "units")
            
    def on_category_mousewheel(self, event):
        if platform.system() == 'Windows':
            self.category_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.category_canvas.xview_scroll(int(-1 * event.delta), "units")

    def create_history_card(self, history_item, card_index):
        # ... (Bu metot önceki halindeki gibi kalacak)
        # Kaydırma çubuğunun gizlendiği hali kullanıyoruz
        card_container = tk.Frame(self.cards_frame, bg="#2d2d2d", padx=2, pady=2)
        card_container.pack(side=tk.LEFT, padx=(0, 10), pady=0)
        
        border_frame = tk.Frame(card_container, bg="#4a90e2", padx=1, pady=1)
        border_frame.pack(fill=tk.BOTH, expand=True)
        
        card_frame = tk.Frame(border_frame, bg="#404040", relief=tk.FLAT, bd=0, 
                              width=320, height=320)
        card_frame.pack(fill=tk.BOTH, expand=True)
        card_frame.pack_propagate(False)
        
        content_frame = tk.Frame(card_frame, bg="#404040")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        header_frame = tk.Frame(content_frame, bg="#404040")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        timestamp = history_item.get('timestamp', 'Unknown')
        if isinstance(timestamp, str) and len(timestamp) > 15:
            timestamp = timestamp[:15] + "..."
        timestamp_label = tk.Label(header_frame, text=timestamp, 
                                   font=("Segoe UI", 9), bg="#404040", fg="#b0b0b0")
        timestamp_label.pack(side=tk.LEFT)

        source = history_item.get('sourceProcess', 'Unknown')
        if len(source) > 12:
            source = source[:12] + "..."
        source_label = tk.Label(header_frame, text=source, 
                                font=("Segoe UI", 9), bg="#404040", fg="#4a90e2")
        source_label.pack(side=tk.RIGHT)
        
        original_text = history_item.get('originalText', '')
        
        text_frame = tk.Frame(content_frame, bg="#404040")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        text_widget = tk.Text(text_frame, bg="#404040", fg="white", 
                              font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
                              wrap=tk.WORD, width=35, height=8)
        text_widget.insert("1.0", original_text)
        text_widget.config(state=tk.DISABLED, cursor="arrow")
        
        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        footer_frame = tk.Frame(content_frame, bg="#404040")
        footer_frame.pack(fill=tk.X)
        
        close_btn = tk.Button(footer_frame, text="✕", font=("Segoe UI", 10), 
                              bg="#dc3545", fg="white", relief=tk.FLAT, bd=0,
                              cursor="hand2", width=2, height=1,
                              command=lambda: self.close_card(card_container, history_item))
        close_btn.pack(side=tk.RIGHT)
        
        unmask_btn = tk.Button(footer_frame, text="⏎", font=("Segoe UI", 10), 
                              bg="#dc3545", fg="white", relief=tk.FLAT, bd=0,
                              cursor="hand2", width=3, height=1,
                              command=lambda: self.unmask_text(history_item))
        unmask_btn.pack(side=tk.LEFT, pady=3, padx=3)

        def on_close_enter(e):
            close_btn.config(bg="#c82333")
        
        def on_close_leave(e):
            close_btn.config(bg="#dc3545")
        
        close_btn.bind("<Enter>", on_close_enter)
        close_btn.bind("<Leave>", on_close_leave)
        
        card_frame.bind("<Button-1>", lambda e, item=history_item: self.copy_to_clipboard(item.get('maskedText', '')))
        content_frame.bind("<Button-1>", lambda e, item=history_item: self.copy_to_clipboard(item.get('maskedText', '')))
        text_widget.bind("<Button-1>", lambda e, item=history_item: self.copy_to_clipboard(item.get('maskedText', '')))
        
        def on_card_enter(e):
            card_frame.config(bg="#505050")
            content_frame.config(bg="#505050")
            header_frame.config(bg="#505050")
            footer_frame.config(bg="#505050")
            timestamp_label.config(bg="#505050")
            source_label.config(bg="#505050")
            text_frame.config(bg="#505050")
            text_widget.config(bg="#505050")
        
        def on_card_leave(e):
            card_frame.config(bg="#404040")
            content_frame.config(bg="#404040")
            header_frame.config(bg="#404040")
            footer_frame.config(bg="#404040")
            timestamp_label.config(bg="#404040")
            source_label.config(bg="#404040")
            text_frame.config(bg="#404040")
            text_widget.config(bg="#404040")
        
        card_frame.bind("<Enter>", on_card_enter)
        card_frame.bind("<Leave>", on_card_leave)
        
        return card_container

    def close_card(self, card_container, history_item):
        card_container.destroy()

    def unmask_text(self, history_item):
        original_text = history_item.get('originalText', '')
        self.copy_to_clipboard(original_text)

    def on_search_focus_in(self, entry):
        if entry.get() == "Search in Original Text":
            entry.delete(0, tk.END)
            entry.config(fg="white")

    def on_search_focus_out(self, entry):
        if entry.get() == "":
            entry.insert(0, "Search in Original Text")
            entry.config(fg="#b0b0b0")

    def on_search_change(self, *args):
        self.refresh_history()

    def on_category_click(self, category):
        print(f"Category clicked: {category}")

    def disable_features(self):
        messagebox.showinfo("Features", "Features disabled")

    def show_menu(self):
        menu = tk.Menu(self.frame, tearoff=0, bg="#2d2d2d", fg="white",
                       activebackground="#4a90e2", activeforeground="white",
                       font=("Segoe UI", 10))
        menu.add_command(label="Refresh", command=self.refresh_history)
        menu.add_command(label="Clear All History", command=self.clear_all_history)
        menu.add_separator()
        menu.add_command(label="Settings", command=self.open_settings)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.close_application)
        
        try:
            menu.tk_popup(self.frame.winfo_pointerx(), self.frame.winfo_pointery())
        finally:
            menu.grab_release()

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
            
            self.on_frame_configure()
            
        except Exception as e:
            print(f"Error refreshing history: {e}")

    def copy_to_clipboard(self, text):
        import pyperclip
        pyperclip.copy(text)

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
        if not self.cards_frame:
            self.create_layout()
        if self.auto_refresh_enabled:
            self.start_auto_refresh()

    def hide(self):
        self.frame.pack_forget()
        self.stop_auto_refresh()