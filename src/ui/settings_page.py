import tkinter as tk
from tkinter import ttk, messagebox
from src.db.clipboard_repository import ClipboardRepository

class SettingsPage:
    def __init__(self, parent, config_service):
        self.frame = tk.Frame(parent)
        self.config_service = config_service
        self.db = ClipboardRepository()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_general_tab()
        self.create_masking_tab()
        self.create_ai_tab()
        self.create_trusted_programs_tab()
        self.create_custom_regex_tab()
        self.create_code_protection_tab()
        
        # Create save/cancel buttons
        self.create_buttons()

    def create_general_tab(self):
        """Create general settings tab"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")
        
        # Create scrollable frame
        canvas = tk.Canvas(general_frame)
        scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # General Settings
        general_label = ttk.Label(scrollable_frame, text="General Settings", font=("Arial", 14, "bold"))
        general_label.pack(pady=(0, 20))
        
        # Disable all features
        self.disable_all_features_var = tk.BooleanVar(value=self.config_service.disable_all_features)
        disable_all_cb = ttk.Checkbutton(scrollable_frame, text="Disable All Features", 
                                        variable=self.disable_all_features_var)
        disable_all_cb.pack(anchor="w", pady=2)
        
        # Disable masking
        self.disable_masking_var = tk.BooleanVar(value=self.config_service.disable_masking)
        disable_masking_cb = ttk.Checkbutton(scrollable_frame, text="Disable Masking", 
                                           variable=self.disable_masking_var)
        disable_masking_cb.pack(anchor="w", pady=2)
        
        # Dark mode
        self.dark_mode_var = tk.BooleanVar(value=self.config_service.darkMode)
        dark_mode_cb = ttk.Checkbutton(scrollable_frame, text="Dark Mode", 
                                     variable=self.dark_mode_var)
        dark_mode_cb.pack(anchor="w", pady=2)
        
        # Show progress bar
        self.show_progress_bar_var = tk.BooleanVar(value=self.config_service.show_progress_bar)
        progress_cb = ttk.Checkbutton(scrollable_frame, text="Show Progress Bar", 
                                    variable=self.show_progress_bar_var)
        progress_cb.pack(anchor="w", pady=2)
        
        # Progress bar times
        progress_frame = ttk.LabelFrame(scrollable_frame, text="Progress Bar Times (minutes)")
        progress_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Inner frame for padding
        progress_inner_frame = ttk.Frame(progress_frame)
        progress_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Short model time
        ttk.Label(progress_inner_frame, text="Short Model:").grid(row=0, column=0, sticky="w", pady=2)
        self.short_model_time_var = tk.StringVar(value=str(self.config_service.progress_bar_time_minutes_for_short_model))
        short_model_entry = ttk.Entry(progress_inner_frame, textvariable=self.short_model_time_var, width=10)
        short_model_entry.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # Medium model time
        ttk.Label(progress_inner_frame, text="Medium Model:").grid(row=1, column=0, sticky="w", pady=2)
        self.medium_model_time_var = tk.StringVar(value=str(self.config_service.progress_bar_time_minutes_for_medium_model))
        medium_model_entry = ttk.Entry(progress_inner_frame, textvariable=self.medium_model_time_var, width=10)
        medium_model_entry.grid(row=1, column=1, padx=(10, 0), pady=2)
        
        # Long model time
        ttk.Label(progress_inner_frame, text="Long Model:").grid(row=2, column=0, sticky="w", pady=2)
        self.long_model_time_var = tk.StringVar(value=str(self.config_service.progress_bar_time_minutes_for_long_model))
        long_model_entry = ttk.Entry(progress_inner_frame, textvariable=self.long_model_time_var, width=10)
        long_model_entry.grid(row=2, column=1, padx=(10, 0), pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_masking_tab(self):
        """Create masking settings tab"""
        masking_frame = ttk.Frame(self.notebook)
        self.notebook.add(masking_frame, text="Masking")
        
        # Create scrollable frame
        canvas = tk.Canvas(masking_frame)
        scrollbar = ttk.Scrollbar(masking_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Masking Settings
        masking_label = ttk.Label(scrollable_frame, text="Masking Settings", font=("Arial", 14, "bold"))
        masking_label.pack(pady=(0, 20))
        
        # Email masking
        email_frame = ttk.LabelFrame(scrollable_frame, text="Email Masking")
        email_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Inner frame for padding
        email_inner_frame = ttk.Frame(email_frame)
        email_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.email_enabled_var = tk.BooleanVar(value=self.config_service.email_enabled)
        email_cb = ttk.Checkbutton(email_inner_frame, text="Enable Email Masking", variable=self.email_enabled_var)
        email_cb.pack(anchor="w", pady=2)
        
        ttk.Label(email_inner_frame, text="Mask Type:").pack(anchor="w", pady=(10, 0))
        self.email_mask_type_var = tk.StringVar(value=str(self.config_service.email_mask_type))
        email_type_combo = ttk.Combobox(email_inner_frame, textvariable=self.email_mask_type_var, 
                                       values=["0 - None", "1 - Asterisk", "2 - Defined Text", "3 - Partial"],
                                       state="readonly", width=20)
        email_type_combo.pack(anchor="w", pady=2)
        
        ttk.Label(email_inner_frame, text="Defined Text:").pack(anchor="w", pady=(10, 0))
        self.email_defined_text_var = tk.StringVar(value=self.config_service.email_defined_text)
        email_text_entry = ttk.Entry(email_inner_frame, textvariable=self.email_defined_text_var, width=30)
        email_text_entry.pack(anchor="w", pady=2)
        
        # Phone masking
        phone_frame = ttk.LabelFrame(scrollable_frame, text="Phone Masking")
        phone_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Inner frame for padding
        phone_inner_frame = ttk.Frame(phone_frame)
        phone_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.phone_enabled_var = tk.BooleanVar(value=self.config_service.phone_enabled)
        phone_cb = ttk.Checkbutton(phone_inner_frame, text="Enable Phone Masking", variable=self.phone_enabled_var)
        phone_cb.pack(anchor="w", pady=2)
        
        ttk.Label(phone_inner_frame, text="Mask Type:").pack(anchor="w", pady=(10, 0))
        self.phone_mask_type_var = tk.StringVar(value=str(self.config_service.phone_mask_type))
        phone_type_combo = ttk.Combobox(phone_inner_frame, textvariable=self.phone_mask_type_var,
                                       values=["0 - None", "1 - Asterisk", "2 - Defined Text", "3 - Partial"],
                                       state="readonly", width=20)
        phone_type_combo.pack(anchor="w", pady=2)
        
        ttk.Label(phone_inner_frame, text="Defined Text:").pack(anchor="w", pady=(10, 0))
        self.phone_defined_text_var = tk.StringVar(value=self.config_service.phone_defined_text)
        phone_text_entry = ttk.Entry(phone_inner_frame, textvariable=self.phone_defined_text_var, width=30)
        phone_text_entry.pack(anchor="w", pady=2)
        
        # Minimum character lengths
        length_frame = ttk.LabelFrame(scrollable_frame, text="Minimum Character Lengths")
        length_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # Inner frame for padding
        length_inner_frame = ttk.Frame(length_frame)
        length_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # AI length
        ttk.Label(length_inner_frame, text="AI Processing:").grid(row=0, column=0, sticky="w", pady=2)
        self.min_char_ai_var = tk.StringVar(value=str(self.config_service.min_char_lenght_ai))
        ai_length_entry = ttk.Entry(length_inner_frame, textvariable=self.min_char_ai_var, width=10)
        ai_length_entry.grid(row=0, column=1, padx=(10, 0), pady=2)

        # Code length
        ttk.Label(length_inner_frame, text="Code:").grid(row=3, column=0, sticky="w", pady=2)
        self.min_char_code_var = tk.StringVar(value=str(self.config_service.min_char_lenght_code))
        code_length_entry = ttk.Entry(length_inner_frame, textvariable=self.min_char_code_var, width=10)
        code_length_entry.grid(row=3, column=1, padx=(10, 0), pady=2)
        
        # Custom regex length
        ttk.Label(length_inner_frame, text="Custom Regex:").grid(row=4, column=0, sticky="w", pady=2)
        self.min_char_regex_var = tk.StringVar(value=str(self.config_service.min_char_lenght_custom_regex))
        regex_length_entry = ttk.Entry(length_inner_frame, textvariable=self.min_char_regex_var, width=10)
        regex_length_entry.grid(row=4, column=1, padx=(10, 0), pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_ai_tab(self):
        """Create AI settings tab"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="AI Processing")
        
        # Create scrollable frame
        canvas = tk.Canvas(ai_frame)
        scrollbar = ttk.Scrollbar(ai_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # AI Settings
        ai_label = ttk.Label(scrollable_frame, text="AI Processing Settings", font=("Arial", 14, "bold"))
        ai_label.pack(pady=(0, 20))
        
        # Enable AI
        self.ai_enabled_var = tk.BooleanVar(value=self.config_service.ai_enabled)
        ai_cb = ttk.Checkbutton(scrollable_frame, text="Enable AI Processing", variable=self.ai_enabled_var)
        ai_cb.pack(anchor="w", pady=2)
        
        # Unmask manual
        self.unmask_manual_var = tk.BooleanVar(value=self.config_service.unMaskManual)
        unmask_cb = ttk.Checkbutton(scrollable_frame, text="Manual Unmasking Only", variable=self.unmask_manual_var)
        unmask_cb.pack(anchor="w", pady=2)
        
        # AI Processing Types
        ai_types_frame = ttk.LabelFrame(scrollable_frame, text="AI Processing Types")
        ai_types_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Inner frame for padding
        ai_types_inner_frame = ttk.Frame(ai_types_frame)
        ai_types_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create treeview for AI types
        self.ai_tree = ttk.Treeview(ai_types_inner_frame, columns=("Description", "Short", "Enabled"), show="headings", height=8)
        self.ai_tree.heading("Description", text="Description")
        self.ai_tree.heading("Short", text="Short Description")
        self.ai_tree.heading("Enabled", text="Enabled")
        
        self.ai_tree.column("Description", width=200)
        self.ai_tree.column("Short", width=150)
        self.ai_tree.column("Enabled", width=80)
        
        self.ai_tree.pack(fill=tk.X)
        
        # Load AI types
        self.load_ai_types()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_trusted_programs_tab(self):
        """Create trusted programs tab"""
        trusted_frame = ttk.Frame(self.notebook)
        self.notebook.add(trusted_frame, text="Trusted Programs")
        
        # Create scrollable frame
        canvas = tk.Canvas(trusted_frame)
        scrollbar = ttk.Scrollbar(trusted_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Trusted Programs Settings
        trusted_label = ttk.Label(scrollable_frame, text="Trusted Programs Settings", font=("Arial", 14, "bold"))
        trusted_label.pack(pady=(0, 20))
        
        # Enable trusted programs
        self.trusted_enabled_var = tk.BooleanVar(value=self.config_service.trusted_programs_enabled)
        trusted_cb = ttk.Checkbutton(scrollable_frame, text="Enable Trusted Programs", variable=self.trusted_enabled_var)
        trusted_cb.pack(anchor="w", pady=2)
        
        # Trusted Programs List
        trusted_list_frame = ttk.LabelFrame(scrollable_frame, text="Trusted Programs")
        trusted_list_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Inner frame for padding
        trusted_list_inner_frame = ttk.Frame(trusted_list_frame)
        trusted_list_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create treeview for trusted programs
        self.trusted_tree = ttk.Treeview(trusted_list_inner_frame, columns=("Program", "Enabled", "Deleted"), show="headings", height=8)
        self.trusted_tree.heading("Program", text="Program Name")
        self.trusted_tree.heading("Enabled", text="Enabled")
        self.trusted_tree.heading("Deleted", text="Deleted")
        
        self.trusted_tree.column("Program", width=300)
        self.trusted_tree.column("Enabled", width=80)
        self.trusted_tree.column("Deleted", width=80)
        
        self.trusted_tree.pack(fill=tk.X)
        
        # Load trusted programs
        self.load_trusted_programs()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_custom_regex_tab(self):
        """Create custom regex tab"""
        regex_frame = ttk.Frame(self.notebook)
        self.notebook.add(regex_frame, text="Custom Regex")
        
        # Create scrollable frame
        canvas = tk.Canvas(regex_frame)
        scrollbar = ttk.Scrollbar(regex_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Custom Regex Settings
        regex_label = ttk.Label(scrollable_frame, text="Custom Regex Settings", font=("Arial", 14, "bold"))
        regex_label.pack(pady=(0, 20))
        
        # Enable custom regex
        self.regex_enabled_var = tk.BooleanVar(value=self.config_service.custom_regex_enabled)
        regex_cb = ttk.Checkbutton(scrollable_frame, text="Enable Custom Regex", variable=self.regex_enabled_var)
        regex_cb.pack(anchor="w", pady=2)
        
        # Priority settings
        priority_frame = ttk.LabelFrame(scrollable_frame, text="Priority Settings")
        priority_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Inner frame for padding
        priority_inner_frame = ttk.Frame(priority_frame)
        priority_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.regex_priority_ai_var = tk.BooleanVar(value=self.config_service.custom_regex_first_priority_for_ai)
        priority_ai_cb = ttk.Checkbutton(priority_inner_frame, text="Custom Regex First Priority for AI", 
                                       variable=self.regex_priority_ai_var)
        priority_ai_cb.pack(anchor="w", pady=2)
        
        self.regex_priority_code_var = tk.BooleanVar(value=self.config_service.custom_regex_first_priority_for_code)
        priority_code_cb = ttk.Checkbutton(priority_inner_frame, text="Custom Regex First Priority for Code", 
                                         variable=self.regex_priority_code_var)
        priority_code_cb.pack(anchor="w", pady=2)
        
        # Custom Regex Patterns
        patterns_frame = ttk.LabelFrame(scrollable_frame, text="Custom Regex Patterns")
        patterns_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Inner frame for padding
        patterns_inner_frame = ttk.Frame(patterns_frame)
        patterns_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create treeview for patterns
        self.patterns_tree = ttk.Treeview(patterns_inner_frame, columns=("Regex", "Replacement", "Apply For", "Priority", "Enabled"), 
                                        show="headings", height=6)
        self.patterns_tree.heading("Regex", text="Regex Pattern")
        self.patterns_tree.heading("Replacement", text="Replacement")
        self.patterns_tree.heading("Apply For", text="Apply For")
        self.patterns_tree.heading("Priority", text="Priority")
        self.patterns_tree.heading("Enabled", text="Enabled")
        
        self.patterns_tree.column("Regex", width=150)
        self.patterns_tree.column("Replacement", width=100)
        self.patterns_tree.column("Apply For", width=80)
        self.patterns_tree.column("Priority", width=80)
        self.patterns_tree.column("Enabled", width=80)
        
        self.patterns_tree.pack(fill=tk.X)
        
        # Load patterns
        self.load_custom_regex_patterns()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_code_protection_tab(self):
        """Create code protection tab"""
        code_frame = ttk.Frame(self.notebook)
        self.notebook.add(code_frame, text="Code Protection")
        
        # Create scrollable frame
        canvas = tk.Canvas(code_frame)
        scrollbar = ttk.Scrollbar(code_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Code Protection Settings
        code_label = ttk.Label(scrollable_frame, text="Code Protection Settings", font=("Arial", 14, "bold"))
        code_label.pack(pady=(0, 20))
        
        # Enable code protection
        self.code_enabled_var = tk.BooleanVar(value=self.config_service.code_protection_enabled)
        code_cb = ttk.Checkbutton(scrollable_frame, text="Enable Code Protection", variable=self.code_enabled_var)
        code_cb.pack(anchor="w", pady=2)
        
        # Code Protection Types
        code_types_frame = ttk.LabelFrame(scrollable_frame, text="Code Protection Types")
        code_types_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        
        # Inner frame for padding
        code_types_inner_frame = ttk.Frame(code_types_frame)
        code_types_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create treeview for code types
        self.code_tree = ttk.Treeview(code_types_inner_frame, columns=("Type", "Enabled"), show="headings", height=6)
        self.code_tree.heading("Type", text="Protection Type")
        self.code_tree.heading("Enabled", text="Enabled")
        
        self.code_tree.column("Type", width=200)
        self.code_tree.column("Enabled", width=80)
        
        self.code_tree.pack(fill=tk.X)
        
        # Load code types
        self.load_code_protection_types()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_buttons(self):
        """Create save and cancel buttons"""
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_btn = ttk.Button(button_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_settings)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        refresh_btn = ttk.Button(button_frame, text="Refresh from Database", command=self.refresh_from_database)
        refresh_btn.pack(side=tk.LEFT)

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

    def cancel_settings(self):
        """Cancel settings changes"""
        # Reload from database to discard changes
        self.config_service.load_config_from_database()
        messagebox.showinfo("Info", "Settings reverted to last saved state")

    def refresh_from_database(self):
        """Refresh settings from database"""
        self.config_service.load_config_from_database()
        messagebox.showinfo("Info", "Settings refreshed from database")

    def show(self):
        """Show the settings page"""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """Hide the settings page"""
        self.frame.pack_forget() 