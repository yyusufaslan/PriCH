import tkinter as tk
from tkinter import ttk, messagebox
from src.db.clipboard_repository import ClipboardRepository

class SettingsPage:
    def __init__(self, parent, config_service, main_window=None):
        self.frame = tk.Frame(parent, bg="#1a1a1a")  # Dark background
        self.config_service = config_service
        self.main_window = main_window  # Store reference to main window
        self.db = ClipboardRepository()
        
        # Create the main layout
        self.create_layout()

    def create_layout(self):
        """Create the main layout with header and scrollable content area"""
        # Create header section
        self.create_header()
        
        # Create main content area with horizontal scrolling
        self.create_scrollable_content()
        
        # Create settings cards
        self.create_settings_cards()

    def create_header(self):
        """Create the header section with title and buttons"""
        # Main header container with gradient effect
        header_container = tk.Frame(self.frame, bg="#2d2d2d", height=35)
        header_container.pack(fill=tk.X, padx=0, pady=0)
        header_container.pack_propagate(False)
        
        # Inner header frame with padding
        header_frame = tk.Frame(header_container, bg="#2d2d2d")
        header_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        # Right section - Buttons
        right_section = tk.Frame(header_frame, bg="#2d2d2d")
        right_section.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Menu button (left side of right section)
        menu_btn = self.create_modern_button(right_section, "Menu", 
                                            command=self.show_menu, 
                                            bg="#6c757d", fg="white",
                                            font=("Segoe UI", 10), width=5, height=1)
        menu_btn.pack(side=tk.LEFT, padx=(0, 10))

    def create_modern_button(self, parent, text, command, bg="#4a90e2", fg="white", 
                           font=("Segoe UI", 10), width=None, height=None):
        """Create a modern button with hover effects"""
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, 
                       font=font, relief=tk.FLAT, bd=0, cursor="hand2",
                       width=width, height=height, padx=5, pady=3)
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=self.lighten_color(bg, 20))
        
        def on_leave(e):
            btn.config(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def lighten_color(self, color, amount):
        """Lighten a hex color by a given amount"""
        # Convert hex to RGB
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        rgb = tuple(min(255, c + amount) for c in rgb)
        
        # Convert back to hex
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def create_scrollable_content(self):
        """Create the horizontally scrollable content area"""
        # Create canvas for horizontal scrolling
        canvas_frame = tk.Frame(self.frame, bg="#1a1a1a")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 5))
        
        self.canvas = tk.Canvas(canvas_frame, bg="#1a1a1a", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        # Create frame for cards inside canvas
        self.cards_frame = tk.Frame(self.canvas, bg="#1a1a1a")
        
        # Configure canvas
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        # Bind events for scrolling
        self.cards_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mouse wheel for horizontal scrolling
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self.on_mousewheel)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_frame_configure(self, event=None):
        """Configure the scroll region when the frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Configure the canvas when it's resized"""
        # Update the width of the cards frame to match canvas width
        canvas_items = self.canvas.find_withtag("all")
        if canvas_items:
            self.canvas.itemconfig(canvas_items[0], width=event.width)

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Scroll horizontally with mouse wheel
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_settings_cards(self):
        """Create all settings cards"""
        self.create_general_card()
        self.create_masking_card()
        self.create_ai_card()
        self.create_trusted_programs_card()
        self.create_custom_regex_card()
        self.create_code_protection_card()

    def create_settings_card(self, title, width=350, height=450):
        """Create a base settings card with modern design"""
        # Create card container with shadow effect
        card_container = tk.Frame(self.cards_frame, bg="#2d2d2d", padx=2, pady=0)
        card_container.pack(side=tk.LEFT, padx=(0, 10), pady=0)
        
        # Add a subtle border for better visibility
        border_frame = tk.Frame(card_container, bg="#4a90e2", padx=1, pady=1)
        border_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main card frame with modern design
        card_frame = tk.Frame(border_frame, bg="#404040", relief=tk.FLAT, bd=0, 
                             width=width, height=height)
        card_frame.pack(fill=tk.BOTH, expand=True)
        card_frame.pack_propagate(False)
        
        # Content frame with padding
        content_frame = tk.Frame(card_frame, bg="#404040")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header section with title
        header_frame = tk.Frame(content_frame, bg="#404040")
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = tk.Label(header_frame, text=title, 
                              font=("Segoe UI", 10, "bold"), 
                              bg="#404040", fg="white")
        title_label.pack(anchor="w")
        
        # Create scrollable frame for content
        canvas = tk.Canvas(content_frame, bg="#404040", highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#404040")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Hover effects for card
        def on_card_enter(e):
            card_frame.config(bg="#505050")
            content_frame.config(bg="#505050")
            header_frame.config(bg="#505050")
            title_label.config(bg="#505050")
            canvas.config(bg="#505050")
            scrollable_frame.config(bg="#505050")
        
        def on_card_leave(e):
            card_frame.config(bg="#404040")
            content_frame.config(bg="#404040")
            header_frame.config(bg="#404040")
            title_label.config(bg="#404040")
            canvas.config(bg="#404040")
            scrollable_frame.config(bg="#404040")
        
        card_frame.bind("<Enter>", on_card_enter)
        card_frame.bind("<Leave>", on_card_leave)
        
        return scrollable_frame

    def create_general_card(self):
        """Create general settings card"""
        content_frame = self.create_settings_card("General Settings", 350, 350)
        
        # Disable all features
        self.disable_all_features_var = tk.BooleanVar(value=self.config_service.disable_all_features)
        disable_all_cb = self.create_checkbox(content_frame, "Disable All Features", self.disable_all_features_var)
        disable_all_cb.pack(anchor="w", pady=2)
        
        # Disable masking
        self.disable_masking_var = tk.BooleanVar(value=self.config_service.disable_masking)
        disable_masking_cb = self.create_checkbox(content_frame, "Disable Masking", self.disable_masking_var)
        disable_masking_cb.pack(anchor="w", pady=2)
        
        # Dark mode
        self.dark_mode_var = tk.BooleanVar(value=self.config_service.darkMode)
        dark_mode_cb = self.create_checkbox(content_frame, "Dark Mode", self.dark_mode_var)
        dark_mode_cb.pack(anchor="w", pady=2)
        
        # Show progress bar
        self.show_progress_bar_var = tk.BooleanVar(value=self.config_service.show_progress_bar)
        progress_cb = self.create_checkbox(content_frame, "Show Progress Bar", self.show_progress_bar_var)
        progress_cb.pack(anchor="w", pady=2)
        
        # Progress bar times section
        self.create_section_label(content_frame, "Progress Bar Times (minutes)")
        
        # Short model time
        self.create_input_field(content_frame, "Short Model:", 
                               tk.StringVar(value=str(self.config_service.progress_bar_time_minutes_for_short_model)),
                               "short_model_time_var")
        
        # Medium model time
        self.create_input_field(content_frame, "Medium Model:", 
                               tk.StringVar(value=str(self.config_service.progress_bar_time_minutes_for_medium_model)),
                               "medium_model_time_var")
        
        # Long model time
        self.create_input_field(content_frame, "Long Model:", 
                               tk.StringVar(value=str(self.config_service.progress_bar_time_minutes_for_long_model)),
                               "long_model_time_var")

    def create_masking_card(self):
        """Create masking settings card"""
        content_frame = self.create_settings_card("Masking Settings", 350, 350)
        
        # Email masking section
        self.create_section_label(content_frame, "Email Masking")
        
        self.email_enabled_var = tk.BooleanVar(value=self.config_service.email_enabled)
        email_cb = self.create_checkbox(content_frame, "Enable Email Masking", self.email_enabled_var)
        email_cb.pack(anchor="w", pady=2)
        
        self.create_combobox_field(content_frame, "Mask Type:", 
                                  tk.StringVar(value=str(self.config_service.email_mask_type)),
                                  ["0 - None", "1 - Asterisk", "2 - Defined Text", "3 - Partial"],
                                  "email_mask_type_var")
        
        self.create_input_field(content_frame, "Defined Text:", 
                               tk.StringVar(value=self.config_service.email_defined_text),
                               "email_defined_text_var")
        
        # Phone masking section
        self.create_section_label(content_frame, "Phone Masking")
        
        self.phone_enabled_var = tk.BooleanVar(value=self.config_service.phone_enabled)
        phone_cb = self.create_checkbox(content_frame, "Enable Phone Masking", self.phone_enabled_var)
        phone_cb.pack(anchor="w", pady=2)
        
        self.create_combobox_field(content_frame, "Mask Type:", 
                                  tk.StringVar(value=str(self.config_service.phone_mask_type)),
                                  ["0 - None", "1 - Asterisk", "2 - Defined Text", "3 - Partial"],
                                  "phone_mask_type_var")
        
        self.create_input_field(content_frame, "Defined Text:", 
                               tk.StringVar(value=self.config_service.phone_defined_text),
                               "phone_defined_text_var")
        
        # Minimum character lengths section
        self.create_section_label(content_frame, "Minimum Character Lengths")
        
        self.create_input_field(content_frame, "AI Processing:", 
                               tk.StringVar(value=str(self.config_service.min_char_lenght_ai)),
                               "min_char_ai_var")
        
        self.create_input_field(content_frame, "Code:", 
                               tk.StringVar(value=str(self.config_service.min_char_lenght_code)),
                               "min_char_code_var")
        
        self.create_input_field(content_frame, "Custom Regex:", 
                               tk.StringVar(value=str(self.config_service.min_char_lenght_custom_regex)),
                               "min_char_regex_var")

    def create_ai_card(self):
        """Create AI settings card"""
        content_frame = self.create_settings_card("AI Processing", 350, 350)
        
        # Enable AI
        self.ai_enabled_var = tk.BooleanVar(value=self.config_service.ai_enabled)
        ai_cb = self.create_checkbox(content_frame, "Enable AI Processing", self.ai_enabled_var)
        ai_cb.pack(anchor="w", pady=2)
        
        # Unmask manual
        self.unmask_manual_var = tk.BooleanVar(value=self.config_service.unMaskManual)
        unmask_cb = self.create_checkbox(content_frame, "Manual Unmasking Only", self.unmask_manual_var)
        unmask_cb.pack(anchor="w", pady=2)
        
        # AI Processing Types section
        self.create_section_label(content_frame, "AI Processing Types")
        
        # Create treeview for AI types
        self.ai_tree = self.create_treeview(content_frame, 
                                           columns=("Description", "Short", "Enabled"),
                                           headings=("Description", "Short Description", "Enabled"),
                                           widths=(200, 150, 80),
                                           height=8)
        
        # Load AI types
        self.load_ai_types()

    def create_trusted_programs_card(self):
        """Create trusted programs card"""
        content_frame = self.create_settings_card("Trusted Programs", 350, 350)
        
        # Enable trusted programs
        self.trusted_enabled_var = tk.BooleanVar(value=self.config_service.trusted_programs_enabled)
        trusted_cb = self.create_checkbox(content_frame, "Enable Trusted Programs", self.trusted_enabled_var)
        trusted_cb.pack(anchor="w", pady=2)
        
        # Trusted Programs section
        self.create_section_label(content_frame, "Trusted Programs")
        
        # Create treeview for trusted programs
        self.trusted_tree = self.create_treeview(content_frame, 
                                                columns=("Program", "Enabled", "Deleted"),
                                                headings=("Program Name", "Enabled", "Deleted"),
                                                widths=(300, 80, 80),
                                                height=8)
        
        # Load trusted programs
        self.load_trusted_programs()

    def create_custom_regex_card(self):
        """Create custom regex card"""
        content_frame = self.create_settings_card("Custom Regex", 350, 350)
        
        # Enable custom regex
        self.regex_enabled_var = tk.BooleanVar(value=self.config_service.custom_regex_enabled)
        regex_cb = self.create_checkbox(content_frame, "Enable Custom Regex", self.regex_enabled_var)
        regex_cb.pack(anchor="w", pady=2)
        
        # Priority settings section
        self.create_section_label(content_frame, "Priority Settings")
        
        self.regex_priority_ai_var = tk.BooleanVar(value=self.config_service.custom_regex_first_priority_for_ai)
        priority_ai_cb = self.create_checkbox(content_frame, "Custom Regex First Priority for AI", self.regex_priority_ai_var)
        priority_ai_cb.pack(anchor="w", pady=2)
        
        self.regex_priority_code_var = tk.BooleanVar(value=self.config_service.custom_regex_first_priority_for_code)
        priority_code_cb = self.create_checkbox(content_frame, "Custom Regex First Priority for Code", self.regex_priority_code_var)
        priority_code_cb.pack(anchor="w", pady=2)
        
        # Custom Regex Patterns section
        self.create_section_label(content_frame, "Custom Regex Patterns")
        
        # Create treeview for patterns
        self.patterns_tree = self.create_treeview(content_frame, 
                                                 columns=("Regex", "Replacement", "Apply For", "Priority", "Enabled"),
                                                 headings=("Regex Pattern", "Replacement", "Apply For", "Priority", "Enabled"),
                                                 widths=(150, 100, 80, 80, 80),
                                                 height=6)
        
        # Load patterns
        self.load_custom_regex_patterns()

    def create_code_protection_card(self):
        """Create code protection card"""
        content_frame = self.create_settings_card("Code Protection", 350, 350)
        
        # Enable code protection
        self.code_enabled_var = tk.BooleanVar(value=self.config_service.code_protection_enabled)
        code_cb = self.create_checkbox(content_frame, "Enable Code Protection", self.code_enabled_var)
        code_cb.pack(anchor="w", pady=2)
        
        # Code Protection Types section
        self.create_section_label(content_frame, "Code Protection Types")
        
        # Create treeview for code types
        self.code_tree = self.create_treeview(content_frame, 
                                             columns=("Type", "Enabled"),
                                             headings=("Protection Type", "Enabled"),
                                             widths=(200, 80),
                                             height=6)
        
        # Load code types
        self.load_code_protection_types()

    def create_checkbox(self, parent, text, variable):
        """Create a modern checkbox"""
        cb = tk.Checkbutton(parent, text=text, variable=variable, 
                           font=("Segoe UI", 10), bg="#404040", fg="white", 
                           selectcolor="#404040", activebackground="#404040", 
                           activeforeground="white", relief=tk.FLAT, bd=0)
        return cb

    def create_section_label(self, parent, text):
        """Create a section label"""
        label = tk.Label(parent, text=text, 
                        font=("Segoe UI", 11, "bold"), 
                        bg="#404040", fg="#4a90e2")
        label.pack(anchor="w", pady=(15, 5))

    def create_input_field(self, parent, label_text, variable, var_reference):
        """Create an input field with label"""
        frame = tk.Frame(parent, bg="#404040")
        frame.pack(fill=tk.X, pady=2)
        
        label = tk.Label(frame, text=label_text, 
                        font=("Segoe UI", 10), 
                        bg="#404040", fg="white")
        label.pack(side=tk.LEFT)
        
        entry = tk.Entry(frame, textvariable=variable, 
                        font=("Segoe UI", 10), width=15,
                        bg="#505050", fg="white", insertbackground="white",
                        relief=tk.FLAT, bd=0)
        entry.pack(side=tk.RIGHT)
        
        # Store reference to variable
        setattr(self, var_reference, variable)
        
        return frame

    def create_combobox_field(self, parent, label_text, variable, values, var_reference):
        """Create a combobox field with label"""
        frame = tk.Frame(parent, bg="#404040")
        frame.pack(fill=tk.X, pady=2)
        
        label = tk.Label(frame, text=label_text, 
                        font=("Segoe UI", 10), 
                        bg="#404040", fg="white")
        label.pack(side=tk.LEFT)
        
        combo = ttk.Combobox(frame, textvariable=variable, 
                            values=values, state="readonly", width=20,
                            font=("Segoe UI", 10))
        combo.pack(side=tk.RIGHT)
        
        # Store reference to variable
        setattr(self, var_reference, variable)
        
        return frame

    def create_treeview(self, parent, columns, headings, widths, height):
        """Create a modern treeview"""
        # Create frame for treeview
        tree_frame = tk.Frame(parent, bg="#404040")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=height)
        
        # Configure headings and columns
        for col, heading, width in zip(columns, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                       background="#505050", 
                       foreground="white", 
                       fieldbackground="#505050",
                       font=("Segoe UI", 9))
        style.configure("Treeview.Heading", 
                       background="#404040", 
                       foreground="white",
                       font=("Segoe UI", 9, "bold"))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        return tree

    def load_ai_types(self):
        """Load AI processing types into treeview"""
        for item in self.ai_tree.get_children():
            self.ai_tree.delete(item)
        
        ai_types = self.config_service.aiProcessingTypes
        for ai_type in ai_types:
            self.ai_tree.insert("", "end", values=(
                ai_type['description'],  # description
                ai_type['shortDescription'],  # short_description
                "Yes" if ai_type['enabled'] else "No"  # enabled
            ))

    def load_trusted_programs(self):
        """Load trusted programs into treeview"""
        for item in self.trusted_tree.get_children():
            self.trusted_tree.delete(item)
        
        trusted_programs = self.config_service.trustedPrograms
        for program in trusted_programs:
            self.trusted_tree.insert("", "end", values=(
                program['programName'],  # program_name
                "Yes" if program['enabled'] else "No",  # enabled
                "Yes" if program['deleted'] else "No"   # deleted
            ))

    def load_custom_regex_patterns(self):
        """Load custom regex patterns into treeview"""
        for item in self.patterns_tree.get_children():
            self.patterns_tree.delete(item)
        
        patterns = self.config_service.customRegexPatterns
        for pattern in patterns:
            self.patterns_tree.insert("", "end", values=(
                pattern['regex'],  # regex
                pattern['replacement'],  # replacement
                pattern['applyFor'],  # apply_for
                "Yes" if pattern['firstPriority'] else "No",  # first_priority
                "Yes" if pattern['enabled'] else "No"   # enabled
            ))

    def load_code_protection_types(self):
        """Load code protection types into treeview"""
        for item in self.code_tree.get_children():
            self.code_tree.delete(item)
        
        code_types = self.config_service.codeProtectionTypes
        for code_type in code_types:
            self.code_tree.insert("", "end", values=(
                code_type['typeName'],  # type_name
                "Yes" if code_type['enabled'] else "No"  # enabled
            ))

    def save_settings(self):
        """Save all settings to database"""
        try:
            # Update config service with current values
            self.config_service.disable_all_features = self.disable_all_features_var.get()
            self.config_service.disable_masking = self.disable_masking_var.get()
            self.config_service.darkMode = self.dark_mode_var.get()
            self.config_service.trusted_programs_enabled = self.trusted_enabled_var.get()
            self.config_service.unMaskManual = self.unmask_manual_var.get()
            self.config_service.show_progress_bar = self.show_progress_bar_var.get()
            
            # Progress bar times
            self.config_service.progress_bar_time_minutes_for_short_model = int(self.short_model_time_var.get())
            self.config_service.progress_bar_time_minutes_for_medium_model = int(self.medium_model_time_var.get())
            self.config_service.progress_bar_time_minutes_for_long_model = int(self.long_model_time_var.get())
            
            # Email settings
            self.config_service.email_enabled = self.email_enabled_var.get()
            self.config_service.email_mask_type = int(self.email_mask_type_var.get().split()[0])
            self.config_service.email_defined_text = self.email_defined_text_var.get()
            
            # Phone settings
            self.config_service.phone_enabled = self.phone_enabled_var.get()
            self.config_service.phone_mask_type = int(self.phone_mask_type_var.get().split()[0])
            self.config_service.phone_defined_text = self.phone_defined_text_var.get()
            
            # AI settings
            self.config_service.ai_enabled = self.ai_enabled_var.get()
            
            # Custom regex settings
            self.config_service.custom_regex_enabled = self.regex_enabled_var.get()
            self.config_service.custom_regex_first_priority_for_ai = self.regex_priority_ai_var.get()
            self.config_service.custom_regex_first_priority_for_code = self.regex_priority_code_var.get()
            
            # Code protection settings
            self.config_service.code_protection_enabled = self.code_enabled_var.get()
            
            # Minimum character lengths
            self.config_service.min_char_lenght_ai = int(self.min_char_ai_var.get())
            self.config_service.min_char_lenght_code = int(self.min_char_code_var.get())
            self.config_service.min_char_lenght_custom_regex = int(self.min_char_regex_var.get())
            
            # Save to database
            self.config_service.save_config_to_database()
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def show_menu(self):
        """Show context menu"""
        menu = tk.Menu(self.frame, tearoff=0, bg="#2d2d2d", fg="white",
                      activebackground="#4a90e2", activeforeground="white",
                      font=("Segoe UI", 10))
        menu.add_command(label="History", command=self.open_history)
        menu.add_separator()
        menu.add_command(label="Save Settings", command=self.save_settings)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.close_application)
        
        # Show menu at cursor position
        try:
            menu.tk_popup(self.frame.winfo_pointerx(), self.frame.winfo_pointery())
        finally:
            menu.grab_release()

    def open_history(self):
        """Open history page"""
        try:
            if self.main_window:
                self.main_window.show_history_page()
            else:
                print("Warning: Main window reference not available")
                messagebox.showwarning("History", "Unable to open history page. Please try again.")
        except Exception as e:
            print(f"Error opening history: {e}")
            messagebox.showerror("Error", f"Failed to open history page: {str(e)}")

    def close_application(self):
        """Close the application"""
        try:
            root = self.frame.winfo_toplevel()
            root.quit()
        except Exception as e:
            print(f"Error closing application: {e}")

    def show(self):
        """Show the settings page"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """Hide the settings page"""
        self.frame.pack_forget() 