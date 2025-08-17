import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from src.db.clipboard_repository import ClipboardRepository

class SettingsPage:
    def __init__(self, parent, config_service, main_window=None):
        self.frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        self.config_service = config_service
        self.main_window = main_window
        self.db = ClipboardRepository()
        
        # Configure customtkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
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
        # Main header container
        header_container = ctk.CTkFrame(self.frame, fg_color="#2d2d2d", height=35)
        header_container.pack(fill="x", padx=0, pady=0)
        header_container.pack_propagate(False)
        
        # Inner header frame with padding
        header_frame = ctk.CTkFrame(header_container, fg_color="#2d2d2d")
        header_frame.pack(fill="both", padx=10, pady=5)
        
        # Right section - Buttons
        right_section = ctk.CTkFrame(header_frame, fg_color="#2d2d2d")
        right_section.pack(side="right", fill="y")
        
        # Menu button
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
        menu_btn.pack(side="left", padx=(0, 10))

    def create_scrollable_content(self):
        """Create the horizontally scrollable content area"""
        # Create scrollable frame for cards
        self.cards_frame = ctk.CTkScrollableFrame(
            self.frame,
            fg_color="#1a1a1a",
            orientation="horizontal"
        )
        self.cards_frame.pack(fill="both", expand=True, padx=10, pady=(5, 5))

    def create_settings_cards(self):
        """Create all settings cards"""
        self.create_general_card()
        self.create_masking_card()
        self.create_ai_card()
        self.create_trusted_programs_card()
        self.create_custom_regex_card()
        self.create_code_protection_card()

    def create_settings_card(self, title, width=350, height=350):
        """Create a base settings card with modern design"""
        # Create card container
        card_container = ctk.CTkFrame(self.cards_frame, fg_color="#2d2d2d", width=width, height=height)
        card_container.pack(side="left", padx=(0, 10), pady=0)
        card_container.pack_propagate(False)
        
        # Content frame with padding
        content_frame = ctk.CTkFrame(card_container, fg_color="#404040")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header section with title
        header_frame = ctk.CTkFrame(content_frame, fg_color="#404040")
        header_frame.pack(fill="x", pady=(0, 5))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#404040",
            text_color="white"
        )
        title_label.pack(anchor="w")
        
        # Create scrollable frame for content
        scrollable_frame = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="#404040"
        )
        scrollable_frame.pack(fill="both", expand=True)
        
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
        cb = ctk.CTkCheckBox(
            parent, 
            text=text, 
            variable=variable,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#4a90e2",
            hover_color="#357abd",
            text_color="white"
        )
        return cb

    def create_section_label(self, parent, text):
        """Create a section label"""
        label = ctk.CTkLabel(
            parent, 
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#404040",
            text_color="#4a90e2"
        )
        label.pack(anchor="w", pady=(15, 5))

    def create_input_field(self, parent, label_text, variable, var_reference):
        """Create an input field with label"""
        frame = ctk.CTkFrame(parent, fg_color="#404040")
        frame.pack(fill="x", pady=2)
        
        label = ctk.CTkLabel(
            frame, 
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#404040",
            text_color="white"
        )
        label.pack(side="left")
        
        entry = ctk.CTkEntry(
            frame, 
            textvariable=variable,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            width=150,
            height=25,
            fg_color="#505050",
            text_color="white",
            border_color="#505050"
        )
        entry.pack(side="right")
        
        # Store reference to variable
        setattr(self, var_reference, variable)
        
        return frame

    def create_combobox_field(self, parent, label_text, variable, values, var_reference):
        """Create a combobox field with label"""
        frame = ctk.CTkFrame(parent, fg_color="#404040")
        frame.pack(fill="x", pady=2)
        
        label = ctk.CTkLabel(
            frame, 
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#404040",
            text_color="white"
        )
        label.pack(side="left")
        
        combo = ctk.CTkOptionMenu(
            frame, 
            variable=variable,
            values=values,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            width=200,
            height=25,
            fg_color="#505050",
            button_color="#4a90e2",
            button_hover_color="#357abd",
            text_color="white"
        )
        combo.pack(side="right")
        
        # Store reference to variable
        setattr(self, var_reference, variable)
        
        return frame

    def create_treeview(self, parent, columns, headings, widths, height):
        """Create a modern treeview using CTkFrame and CTkTextbox for display"""
        # Create frame for treeview
        tree_frame = ctk.CTkFrame(parent, fg_color="#404040")
        tree_frame.pack(fill="both", expand=True, pady=5)
        
        # Create a text widget to display the data in a table format
        text_widget = ctk.CTkTextbox(
            tree_frame,
            fg_color="#505050",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            height=height * 20  # Approximate height based on number of rows
        )
        text_widget.pack(fill="both", expand=True)
        
        # Store the text widget for later use
        text_widget.tree_data = []
        
        return text_widget

    def load_ai_types(self):
        """Load AI processing types into text widget"""
        self.ai_tree.delete("1.0", "end")
        
        # Create header
        header = f"{'Description':<30} {'Short Description':<20} {'Enabled':<10}\n"
        self.ai_tree.insert("1.0", header)
        self.ai_tree.insert("end", "-" * 60 + "\n")
        
        ai_types = self.config_service.aiProcessingTypes
        for ai_type in ai_types:
            row = f"{ai_type['description']:<30} {ai_type['shortDescription']:<20} {'Yes' if ai_type['enabled'] else 'No':<10}\n"
            self.ai_tree.insert("end", row)

    def load_trusted_programs(self):
        """Load trusted programs into text widget"""
        self.trusted_tree.delete("1.0", "end")
        
        # Create header
        header = f"{'Program Name':<30} {'Enabled':<10} {'Deleted':<10}\n"
        self.trusted_tree.insert("1.0", header)
        self.trusted_tree.insert("end", "-" * 50 + "\n")
        
        trusted_programs = self.config_service.trustedPrograms
        for program in trusted_programs:
            row = f"{program['programName']:<30} {'Yes' if program['enabled'] else 'No':<10} {'Yes' if program['deleted'] else 'No':<10}\n"
            self.trusted_tree.insert("end", row)

    def load_custom_regex_patterns(self):
        """Load custom regex patterns into text widget"""
        self.patterns_tree.delete("1.0", "end")
        
        # Create header
        header = f"{'Regex Pattern':<20} {'Replacement':<15} {'Apply For':<12} {'Priority':<10} {'Enabled':<10}\n"
        self.patterns_tree.insert("1.0", header)
        self.patterns_tree.insert("end", "-" * 67 + "\n")
        
        patterns = self.config_service.customRegexPatterns
        for pattern in patterns:
            row = f"{pattern['regex']:<20} {pattern['replacement']:<15} {pattern['applyFor']:<12} {'Yes' if pattern['firstPriority'] else 'No':<10} {'Yes' if pattern['enabled'] else 'No':<10}\n"
            self.patterns_tree.insert("end", row)

    def load_code_protection_types(self):
        """Load code protection types into text widget"""
        self.code_tree.delete("1.0", "end")
        
        # Create header
        header = f"{'Protection Type':<25} {'Enabled':<10}\n"
        self.code_tree.insert("1.0", header)
        self.code_tree.insert("end", "-" * 35 + "\n")
        
        code_types = self.config_service.codeProtectionTypes
        for code_type in code_types:
            row = f"{code_type['typeName']:<25} {'Yes' if code_type['enabled'] else 'No':<10}\n"
            self.code_tree.insert("end", row)

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
        """Show custom menu using CTkToplevel"""
        # Create a custom menu using CTkFrame
        menu_window = ctk.CTkToplevel()
        menu_window.title("Menu")
        menu_window.geometry("200x200")
        menu_window.configure(fg_color="#2d2d2d")
        menu_window.attributes("-topmost", True)
        
        # Center the menu window
        menu_window.update_idletasks()
        x = (menu_window.winfo_screenwidth() // 2) - (200 // 2)
        y = (menu_window.winfo_screenheight() // 2) - (200 // 2)
        menu_window.geometry(f"200x200+{x}+{y}")
        
        menu_frame = ctk.CTkFrame(menu_window, fg_color="#2d2d2d")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Menu buttons
        history_btn = ctk.CTkButton(
            menu_frame,
            text="History",
            command=lambda: [self.open_history(), menu_window.destroy()],
            fg_color="#4a90e2",
            hover_color="#357abd",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=180,
            height=35
        )
        history_btn.pack(pady=5)
        
        save_btn = ctk.CTkButton(
            menu_frame,
            text="Save Settings",
            command=lambda: [self.save_settings(), menu_window.destroy()],
            fg_color="#28a745",
            hover_color="#218838",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=180,
            height=35
        )
        save_btn.pack(pady=5)
        
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
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        """Hide the settings page"""
        self.frame.pack_forget() 