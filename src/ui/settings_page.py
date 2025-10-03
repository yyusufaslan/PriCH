import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from src.ui.tooltip import Tooltip
from src.db.clipboard_repository import ClipboardRepository
from src.utils.scroll_manager import ScrollManager

import tkinter.messagebox as messagebox
from src.ui.tooltip_info import ToolTipInfo

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
        self.menu_btn = ctk.CTkButton(
            right_section, 
            text="≡", 
            command=self.show_menu,
            fg_color="#6c757d",
            hover_color="#5a6268",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=25,
            height=25
        )
        self.menu_btn.pack(side="left", padx=(0, 10))
        Tooltip(self.menu_btn, "Menu")

    def create_scrollable_content(self):
        """Create the horizontally scrollable content area"""
        # Create scrollable frame for cards using ScrollManager
        self.cards_frame = ScrollManager.create_scrollable_cards_container(
            self.frame,
            fg_color="#1a1a1a"
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
        self.create_spacy_card()

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
        
        # Bind mouse wheel events for horizontal scrolling of settings cards
        ScrollManager.bind_horizontal_scroll(card_container)
        ScrollManager.bind_horizontal_scroll(content_frame)
        ScrollManager.bind_horizontal_scroll(scrollable_frame)
        
        return scrollable_frame

    def create_general_card(self):
        """Create general settings card"""
        content_frame = self.create_settings_card("General Settings", 350, 350)
        
        
        # Disable masking
        self.disable_masking_var = tk.BooleanVar(value=self.config_service.disable_masking)
        disable_masking_cb = self.create_checkbox(content_frame, "Disable Masking", self.disable_masking_var)
        disable_masking_cb.pack(anchor="w", pady=2)
        
        # Dark mode
        self.dark_mode_var = tk.BooleanVar(value=self.config_service.darkMode)
        dark_mode_cb = self.create_checkbox(content_frame, "Dark Mode", self.dark_mode_var)
        dark_mode_cb.pack(anchor="w", pady=2)
                
    def create_spacy_card(self):
        """Create spacy settings card, list all spacy models, download, enable just one model, delete model"""
        content_frame = self.create_settings_card("Spacy Settings", 350, 350)
        
        # Spacy models section
        self.create_section_label(content_frame, "Spacy Models")
        
        # Top controls: Enabled Model (downloaded only)
        controls_frame = ctk.CTkFrame(content_frame, fg_color="#404040")
        controls_frame.pack(fill="x", pady=(0, 5))

        label = ctk.CTkLabel(
            controls_frame,
            text="Enabled Model:",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#404040",
            text_color="white"
        )
        label.pack(side="left", padx=(0, 6))

        self._enabled_spacy_model_names = [
            m.get('modelShortName') or m.get('modelName') or ''
            for m in getattr(self.config_service, 'spacyModels', []) if bool(m.get('downloaded'))
        ] or [""]
        # Preselect currently enabled downloaded model if any
        current_enabled = next((m.get('modelShortName') or m.get('modelName') for m in self.config_service.spacyModels if m.get('enabled') and m.get('downloaded')), self._enabled_spacy_model_names[0])
        self.spacy_enabled_select_var = tk.StringVar(value=current_enabled)
        self.spacy_enabled_select_combo = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.spacy_enabled_select_var,
            values=self._enabled_spacy_model_names,
            command=self.on_spacy_enabled_changed,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            width=200,
            height=25,
            fg_color="#505050",
            button_color="#4a90e2",
            button_hover_color="#357abd",
            text_color="white"
        )
        self.spacy_enabled_select_combo.pack(side="left")

        # Spacy models list
        self.create_spacy_models_list(content_frame)
        
    def create_spacy_models_list(self, parent):
        """Create spacy models list, list all spacy models, download, enable just one model, delete model"""
        # Clear previous list if exists
        if hasattr(self, 'spacy_models_list_frame') and self.spacy_models_list_frame is not None:
            try:
                for child in self.spacy_models_list_frame.winfo_children():
                    child.destroy()
                self.spacy_models_list_frame.pack_forget()
            except Exception:
                pass

        self.spacy_models_list_frame = ctk.CTkFrame(parent, fg_color="#404040")
        self.spacy_models_list_frame.pack(fill="both", expand=True, pady=5)

        # Render models from config service if available
        models = getattr(self.config_service, 'spacyModels', []) or []
        if not models:
            empty_label = ctk.CTkLabel(
                self.spacy_models_list_frame,
                text="No spaCy models found in database.",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#cccccc"
            )
            empty_label.pack(pady=10)
            return

        for model in models:
            row = ctk.CTkFrame(self.spacy_models_list_frame, fg_color="#404040")
            row.pack(fill="x", pady=2)

            short_name = model.get('modelShortName') or model.get('modelName') or 'Unknown'
            size_text = model.get('modelSize') or ''
            desc_text = model.get('modelDescription') or ''

            left_frame = ctk.CTkFrame(row, fg_color="#404040")
            left_frame.pack(side="left", fill="x", expand=True)

            title_label = ctk.CTkLabel(
                left_frame,
                text=short_name,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="white"
            )
            title_label.pack(anchor="w")

            status_parts = []
            status_parts.append("enabled" if bool(model.get('enabled')) else "disabled")
            status_parts.append("downloaded" if bool(model.get('downloaded')) else "not downloaded")
            if size_text:
                status_parts.append(str(size_text))
            status = " | ".join(status_parts)

            status_label = ctk.CTkLabel(
                left_frame,
                text=status,
                font=ctk.CTkFont(family="Segoe UI", size=9),
                text_color="#cccccc"
            )
            status_label.pack(anchor="w")

            right_frame = ctk.CTkFrame(row, fg_color="#404040")
            right_frame.pack(side="right")

            if bool(model.get('downloaded')):
                delete_btn = ctk.CTkButton(
                    right_frame,
                    text="Delete",
                    command=lambda sn=short_name: self.on_spacy_row_delete_clicked(sn),
                    font=ctk.CTkFont(family="Segoe UI", size=9),
                    fg_color="#6c757d",
                    hover_color="#5a6268",
                    height=25,
                    width=70
                )
                delete_btn.pack(side="right")
            else:
                download_btn = ctk.CTkButton(
                    right_frame,
                    text="Download",
                    command=lambda sn=short_name: self.on_spacy_row_download_clicked(sn),
                    font=ctk.CTkFont(family="Segoe UI", size=9),
                    fg_color="#4a90e2",
                    hover_color="#357abd",
                    height=25,
                    width=90
                )
                download_btn.pack(side="right")

    def _refresh_spacy_section(self):
        # Refresh enabled combobox values (downloaded only) and list
        self._enabled_spacy_model_names = [
            m.get('modelShortName') or m.get('modelName') or ''
            for m in getattr(self.config_service, 'spacyModels', []) if bool(m.get('downloaded'))
        ] or [""]
        self.spacy_enabled_select_combo.configure(values=self._enabled_spacy_model_names)
        if self.spacy_enabled_select_var.get() not in self._enabled_spacy_model_names:
            self.spacy_enabled_select_var.set(self._enabled_spacy_model_names[0])
        self.create_spacy_models_list(self.spacy_models_list_frame.master)

    def on_spacy_row_download_clicked(self, model_short):
        try:
            model_short = (model_short or "").strip()
            if not model_short:
                messagebox.showerror("Error", "Invalid model name.")
                return
            from src.services.checkers.spacy_checker import SpacyChecker
            checker = SpacyChecker()
            ok = checker.download_spacy_model(model_short)
            if not ok:
                messagebox.showerror("Error", f"Failed to download spaCy model '{model_short}'.")
                return
            if self.config_service.update_spacy_model_flags(model_short, downloaded=True):
                self.config_service.load_config_from_database()
                self._refresh_spacy_section()
                messagebox.showinfo("Success", f"Model '{model_short}' downloaded.")
            else:
                messagebox.showerror("Error", f"Failed to update database for '{model_short}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def on_spacy_row_delete_clicked(self, model_short):
        try:
            model_short = (model_short or "").strip()
            if not model_short:
                messagebox.showerror("Error", "Invalid model name.")
                return
            # Soft delete and disable if currently enabled
            if self.config_service.update_spacy_model_flags(model_short, downloaded=False, enabled=False):
                self.config_service.load_config_from_database()
                self._refresh_spacy_section()
                messagebox.showinfo("Success", f"Model '{model_short}' marked as not downloaded.")
            else:
                messagebox.showerror("Error", f"Failed to update database for '{model_short}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {str(e)}")

    def on_spacy_enabled_changed(self, selected_model_short):
        try:
            selected = (selected_model_short or "").strip()
            if not selected:
                return
            # Enable selected and disable others (downloaded ones)
            for m in list(getattr(self.config_service, 'spacyModels', [])):
                short = m.get('modelShortName') or m.get('modelName') or ''
                if not short:
                    continue
                if bool(m.get('downloaded')):
                    self.config_service.update_spacy_model_flags(short, enabled=(short == selected))
            self.config_service.load_config_from_database()
            self._refresh_spacy_section()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update enabled model: {str(e)}")
        
    def create_masking_card(self):
        """Create masking settings card"""
        content_frame = self.create_settings_card("Masking Settings", 350, 350)
        
        # Email masking section
        self.create_section_label(content_frame, "Email Masking")
        
        self.email_enabled_var = tk.BooleanVar(value=self.config_service.email_enabled)
        email_cb = self.create_checkbox(content_frame, "Enable Email Masking", self.email_enabled_var)
        email_cb.pack(anchor="w", pady=2)
        
        # Email mask type mapping
        self.email_mask_options = ["None", "Asterisk", "Defined Text", "Partial"]
        self.email_mask_values = [0, 1, 2, 3]
        current_email_mask = self.config_service.email_mask_type
        email_display_text = self.email_mask_options[current_email_mask] if current_email_mask < len(self.email_mask_options) else "None"
        
        # Email mask type combobox with callback
        self.email_mask_type_var = tk.StringVar(value=email_display_text)
        self.email_combobox_frame = self.create_combobox_field(content_frame, "Mask Type:", 
                                  self.email_mask_type_var,
                                  self.email_mask_options,
                                  "email_mask_type_var")
        
        # Add callback to email combobox
        email_combobox = self.email_combobox_frame.winfo_children()[-1]  # Get the combobox widget
        email_combobox.configure(command=self.on_email_mask_type_changed)
        
        # Email defined text input (initially hidden)
        self.email_defined_text_var = tk.StringVar(value=self.config_service.email_defined_text)
        self.email_defined_text_frame = self.create_input_field(content_frame, "Defined Text:", 
                               self.email_defined_text_var,
                               "email_defined_text_var")
        
        # Initially hide email defined text if not "Defined Text"
        if email_display_text != "Defined Text":
            self.email_defined_text_frame.pack_forget()
        
        # Phone masking section
        self.create_section_label(content_frame, "Phone Masking")
        
        self.phone_enabled_var = tk.BooleanVar(value=self.config_service.phone_enabled)
        phone_cb = self.create_checkbox(content_frame, "Enable Phone Masking", self.phone_enabled_var)
        phone_cb.pack(anchor="w", pady=2)
        
        # Phone mask type mapping
        self.phone_mask_options = ["None", "Asterisk", "Defined Text", "Partial"]
        self.phone_mask_values = [0, 1, 2, 3]
        current_phone_mask = self.config_service.phone_mask_type
        phone_display_text = self.phone_mask_options[current_phone_mask] if current_phone_mask < len(self.phone_mask_options) else "None"
        
        # Phone mask type combobox with callback
        self.phone_mask_type_var = tk.StringVar(value=phone_display_text)
        self.phone_combobox_frame = self.create_combobox_field(content_frame, "Mask Type:", 
                                  self.phone_mask_type_var,
                                  self.phone_mask_options,
                                  "phone_mask_type_var")
        
        # Add callback to phone combobox
        phone_combobox = self.phone_combobox_frame.winfo_children()[-1]  # Get the combobox widget
        phone_combobox.configure(command=self.on_phone_mask_type_changed)
        
        # Phone defined text input (initially hidden)
        self.phone_defined_text_var = tk.StringVar(value=self.config_service.phone_defined_text)
        self.phone_defined_text_frame = self.create_input_field(content_frame, "Defined Text:", 
                               self.phone_defined_text_var,
                               "phone_defined_text_var")
        
        # Initially hide phone defined text if not "Defined Text"
        if phone_display_text != "Defined Text":
            self.phone_defined_text_frame.pack_forget()
        
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
        
        # Save button for masking settings
        save_button = ctk.CTkButton(
            content_frame,
            text="Save Masking Settings",
            command=self.save_masking_settings,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#4a90e2",
            hover_color="#357abd",
            height=30
        )
        save_button.pack(pady=(15, 5))

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
        
        # Container for interactive toggles
        self.ai_types_container = ctk.CTkFrame(content_frame, fg_color="#404040")
        self.ai_types_container.pack(fill="both", expand=True, pady=5)
        
        # Load interactive list
        self.load_ai_types()

    def create_trusted_programs_card(self):
        """Create trusted programs card"""
        # Create card container manually to have more control
        card_container = ctk.CTkFrame(self.cards_frame, fg_color="#2d2d2d", width=350, height=350)
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
            text="Trusted Programs",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#404040",
            text_color="white"
        )
        title_label.pack(anchor="w")
        
        # Enable trusted programs (outside scrollable frame)
        self.trusted_enabled_var = tk.BooleanVar(value=self.config_service.trusted_programs_enabled)
        trusted_cb = self.create_checkbox(content_frame, "Enable Trusted Programs", self.trusted_enabled_var)
        trusted_cb.pack(anchor="w", pady=2)
        
        # Trusted Programs section
        self.create_section_label(content_frame, "Trusted Programs")
        
        # Search frame (outside scrollable frame)
        search_frame = ctk.CTkFrame(content_frame, fg_color="#404040")
        search_frame.pack(fill="x", pady=(0, 5))
        
        # Search label
        search_label = ctk.CTkLabel(
            search_frame, 
            text="Search:",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#404040",
            text_color="white"
        )
        search_label.pack(side="left", padx=(0, 5))
        
        # Search entry
        self.trusted_search_var = tk.StringVar()
        self.trusted_search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.trusted_search_var,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            width=200,
            height=25,
            fg_color="#505050",
            text_color="white",
            border_color="#505050",
            placeholder_text="Search programs..."
        )
        self.trusted_search_entry.pack(side="left", padx=(0, 5))
        
        # Ensure the search entry can receive focus
        self.trusted_search_entry.bind("<Button-1>", lambda e: self.trusted_search_entry.focus_set())
        self.trusted_search_entry.bind("<FocusIn>", lambda e: self.trusted_search_entry.focus_set())
        
        # Bind search event
        self.trusted_search_var.trace("w", self.on_trusted_search_changed)
        
        # Clear search button
        clear_search_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            command=self.clear_trusted_search,
            font=ctk.CTkFont(family="Segoe UI", size=9),
            width=50,
            height=25,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        clear_search_btn.pack(side="left")
        
        # Create scrollable frame for the patterns list only
        scrollable_frame = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="#404040"
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Container for interactive toggles (inside scrollable frame)
        self.trusted_programs_container = ctk.CTkFrame(scrollable_frame, fg_color="#404040")
        self.trusted_programs_container.pack(fill="both", expand=True, pady=5)

        # Store original programs list for filtering
        self._all_trusted_programs = []
        
        # Load interactive list
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
        
        # Add New button
        self.add_new_btn = ctk.CTkButton(
            content_frame,
            text="Add New Pattern",
            command=self.toggle_add_regex_form,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#4a90e2",
            hover_color="#357abd",
            height=25,
            width=120
        )
        self.add_new_btn.pack(anchor="w", pady=(0, 5))
        
        # Inline form (initially hidden)
        self.regex_form_container = ctk.CTkFrame(content_frame, fg_color="#404040")
        self.regex_form_container.pack(fill="x", pady=(0, 5))
        self.regex_form_container.pack_forget()  # Initially hidden
        
        # Form fields
        form_fields_frame = ctk.CTkFrame(self.regex_form_container, fg_color="#404040")
        form_fields_frame.pack(fill="x", pady=10)
        
        # Regex pattern input
        regex_label = ctk.CTkLabel(form_fields_frame, text="Regex Pattern:", font=ctk.CTkFont(family="Segoe UI", size=10))
        regex_label.pack(anchor="w", pady=(0, 2))
        self.regex_entry = ctk.CTkEntry(form_fields_frame, height=25, placeholder_text="Enter regex pattern...")
        self.regex_entry.pack(fill="x", pady=(0, 10))
        
        # Replacement input
        replacement_label = ctk.CTkLabel(form_fields_frame, text="Replacement:", font=ctk.CTkFont(family="Segoe UI", size=10))
        replacement_label.pack(anchor="w", pady=(0, 2))
        self.replacement_entry = ctk.CTkEntry(form_fields_frame, height=25, placeholder_text="Enter replacement text...")
        self.replacement_entry.pack(fill="x", pady=(0, 10))
        
        # Apply For input
        apply_for_label = ctk.CTkLabel(form_fields_frame, text="Apply For:", font=ctk.CTkFont(family="Segoe UI", size=10))
        apply_for_label.pack(anchor="w", pady=(0, 2))
        self.apply_for_entry = ctk.CTkEntry(form_fields_frame, height=25, placeholder_text="e.g., AI, Code, Both...")
        self.apply_for_entry.pack(fill="x", pady=(0, 10))
        
        # Checkboxes and buttons frame
        controls_frame = ctk.CTkFrame(form_fields_frame, fg_color="#404040")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Checkboxes
        checkboxes_frame = ctk.CTkFrame(controls_frame, fg_color="#404040")
        checkboxes_frame.pack(side="left")
        
        # Enabled checkbox
        self.regex_enabled_var = tk.BooleanVar(value=True)
        enabled_cb = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Enabled",
            variable=self.regex_enabled_var,
            font=ctk.CTkFont(family="Segoe UI", size=10)
        )
        enabled_cb.pack(side="left", padx=(0, 15))
        
        # Priority checkbox
        self.regex_priority_var = tk.BooleanVar(value=False)
        priority_cb = ctk.CTkCheckBox(
            checkboxes_frame,
            text="First Priority",
            variable=self.regex_priority_var,
            font=ctk.CTkFont(family="Segoe UI", size=10)
        )
        priority_cb.pack(side="left")
        
        # Buttons
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="#404040")
        buttons_frame.pack(side="right")
        
        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=self.save_new_regex_pattern_inline,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#4a90e2",
            hover_color="#357abd",
            height=25,
            width=60
        )
        save_btn.pack(side="right", padx=(5, 0))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.hide_add_regex_form,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#6c757d",
            hover_color="#5a6268",
            height=25,
            width=60
        )
        cancel_btn.pack(side="right")
        
        # Container for interactive toggles
        self.regex_patterns_container = ctk.CTkFrame(content_frame, fg_color="#404040")
        self.regex_patterns_container.pack(fill="both", expand=True, pady=5)
        
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
        
        # Container for interactive toggles
        self.code_types_container = ctk.CTkFrame(content_frame, fg_color="#404040")
        self.code_types_container.pack(fill="x", expand=False, pady=5)

        # Load interactive toggles
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
        """Render AI processing types as interactive toggles that persist to DB"""
        # Clear previous children
        for child in getattr(self, 'ai_types_container', []).winfo_children() if hasattr(self, 'ai_types_container') else []:
            child.destroy()
        self._ai_type_vars = {}
        
        ai_types = self.config_service.aiProcessingTypes
        for ai_type in ai_types:
            description = ai_type.get('description', '')
            short_description = ai_type.get('shortDescription', '')
            enabled = bool(ai_type.get('enabled'))
            ai_mask_option = ai_type.get('aiMaskOption')

            row = ctk.CTkFrame(self.ai_types_container, fg_color="#404040")
            row.pack(fill="x", pady=2)

            # Short description label
            short_desc_label = ctk.CTkLabel(
                row, 
                text=short_description, 
                font=ctk.CTkFont(family="Segoe UI", size=10), 
                text_color="white"
            )
            short_desc_label.pack(side="left", padx=(0, 5))

            # Info icon for description hover
            info_label = ctk.CTkLabel(
                row, 
                text="ⓘ",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                text_color="#4a90e2",
                height=25,
                width=25
            )
            info_label.pack(side="left", padx=(0, 10))
            
            # Create tooltip with proper closure to capture the current short_description
            ToolTipInfo(info_label, short_description)

            # Enabled checkbox
            enabled_var = tk.BooleanVar(value=enabled)
            enabled_cb = self.create_checkbox(row, "", enabled_var)
            enabled_cb.configure(command=lambda amo=ai_mask_option, v=enabled_var: self.on_toggle_ai_type(amo, v))
            enabled_cb.pack(side="right", padx=(10, 0))

            self._ai_type_vars[ai_mask_option] = enabled_var

    def load_trusted_programs(self, search_term=""):
        """Render trusted programs as interactive toggles that persist to DB"""
        # Store all programs if not already stored
        if not hasattr(self, '_all_trusted_programs') or not self._all_trusted_programs:
            self._all_trusted_programs = self.config_service.trustedPrograms.copy()
        
        # Filter programs based on search term
        filtered_programs = self._all_trusted_programs
        if search_term:
            search_lower = search_term.lower()
            filtered_programs = [
                program for program in self._all_trusted_programs
                if search_lower in program.get('programName', '').lower()
            ]
        
        # Clear previous children
        for child in getattr(self, 'trusted_programs_container', []).winfo_children() if hasattr(self, 'trusted_programs_container') else []:
            child.destroy()

        self._trusted_vars = {}
        
        # Show "No results" message if no programs match
        if not filtered_programs:
            no_results_label = ctk.CTkLabel(
                self.trusted_programs_container,
                text="No programs found matching search criteria",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#888888"
            )
            no_results_label.pack(pady=20)
            return
        
        for program in filtered_programs:
            name = program.get('programName')
            enabled = bool(program.get('enabled'))
            deleted = bool(program.get('deleted'))

            row = ctk.CTkFrame(self.trusted_programs_container, fg_color="#404040")
            row.pack(fill="x", pady=2)

            name_label = ctk.CTkLabel(row, text=name, font=ctk.CTkFont(family="Segoe UI", size=10), text_color="white")
            name_label.pack(side="left")

            enabled_var = tk.BooleanVar(value=enabled)
            enabled_cb = self.create_checkbox(row, "Enabled", enabled_var)
            enabled_cb.configure(command=lambda pn=name, v=enabled_var: self.on_toggle_trusted_program_enabled(pn, v))
            enabled_cb.pack(side="right", padx=(10, 0))

            deleted_var = tk.BooleanVar(value=deleted)
            deleted_cb = self.create_checkbox(row, "Deleted", deleted_var)
            deleted_cb.configure(command=lambda pn=name, v=deleted_var: self.on_toggle_trusted_program_deleted(pn, v))
            deleted_cb.pack(side="right", padx=(10, 0))

            self._trusted_vars[name] = {"enabled": enabled_var, "deleted": deleted_var}

    def on_toggle_trusted_program_enabled(self, program_name: str, var: tk.BooleanVar):
        new_value = bool(var.get())
        success = self.config_service.update_trusted_program(program_name, enabled=new_value)
        if not success:
            var.set(not new_value)
            messagebox.showerror("Error", f"Failed to update '{program_name}' enabled flag.")

    def on_toggle_trusted_program_deleted(self, program_name: str, var: tk.BooleanVar):
        new_value = bool(var.get())
        success = self.config_service.update_trusted_program(program_name, deleted=new_value)
        if not success:
            var.set(not new_value)
            messagebox.showerror("Error", f"Failed to update '{program_name}' deleted flag.")

    def on_trusted_search_changed(self, *args):
        """Handle search input changes"""
        search_term = self.trusted_search_var.get()
        self.load_trusted_programs(search_term)

    def clear_trusted_search(self):
        """Clear search input and show all programs"""
        self.trusted_search_var.set("")
        self.load_trusted_programs("")

    def on_toggle_ai_type(self, ai_mask_option: int, var: tk.BooleanVar):
        """Handle toggle of an AI processing type and persist change."""
        new_value = bool(var.get())
        success = self.config_service.update_ai_processing_type(ai_mask_option, new_value)
        if not success:
            # Revert UI state if failed
            var.set(not new_value)
            messagebox.showerror("Error", f"Failed to update AI processing type '{ai_mask_option}'.")



    def load_custom_regex_patterns(self):
        """Render custom regex patterns as interactive toggles that persist to DB"""
        # Clear previous children
        for child in getattr(self, 'regex_patterns_container', []).winfo_children() if hasattr(self, 'regex_patterns_container') else []:
            child.destroy()

        self._regex_pattern_vars = {}
        
        patterns = self.config_service.customRegexPatterns
        for pattern in patterns:
            pattern_id = pattern.get('id')
            regex = pattern.get('regex', '')
            replacement = pattern.get('replacement', '')
            apply_for = pattern.get('applyFor', '')
            enabled = bool(pattern.get('enabled'))
            first_priority = bool(pattern.get('firstPriority'))

            # Create main row frame
            row = ctk.CTkFrame(self.regex_patterns_container, fg_color="#404040")
            row.pack(fill="x", pady=2)

            # Left side - Pattern info
            info_frame = ctk.CTkFrame(row, fg_color="#404040")
            info_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

            # Regex pattern (truncated if too long)
            regex_display = regex[:30] + "..." if len(regex) > 30 else regex
            regex_label = ctk.CTkLabel(
                info_frame, 
                text=f"Regex: {regex_display}", 
                font=ctk.CTkFont(family="Segoe UI", size=9), 
                text_color="white"
            )
            regex_label.pack(anchor="w")

            # Replacement and Apply For
            details_text = f"Replace: {replacement[:15]}{'...' if len(replacement) > 15 else ''} | For: {apply_for}"
            details_label = ctk.CTkLabel(
                info_frame, 
                text=details_text, 
                font=ctk.CTkFont(family="Segoe UI", size=8), 
                text_color="#cccccc"
            )
            details_label.pack(anchor="w")

            # Right side - Toggle controls
            controls_frame = ctk.CTkFrame(row, fg_color="#404040")
            controls_frame.pack(side="right")

            # Enabled checkbox
            enabled_var = tk.BooleanVar(value=enabled)
            enabled_cb = self.create_checkbox(controls_frame, "Enabled", enabled_var)
            enabled_cb.configure(command=lambda pid=pattern_id, v=enabled_var: self.on_toggle_regex_enabled(pid, v))
            enabled_cb.pack(side="right", padx=(5, 0))

            # Priority checkbox
            priority_var = tk.BooleanVar(value=first_priority)
            priority_cb = self.create_checkbox(controls_frame, "Priority", priority_var)
            priority_cb.configure(command=lambda pid=pattern_id, v=priority_var: self.on_toggle_regex_priority(pid, v))
            priority_cb.pack(side="right", padx=(5, 0))

            self._regex_pattern_vars[pattern_id] = {"enabled": enabled_var, "priority": priority_var}

    def load_code_protection_types(self):
        """Render code protection types as toggles that persist to DB"""
        # Clear previous children
        for child in getattr(self, 'code_types_container', []).winfo_children() if hasattr(self, 'code_types_container') else []:
            child.destroy()

        self._code_type_vars = {}
        for code_type in self.config_service.codeProtectionTypes:
            type_name = code_type.get('typeName')
            enabled = bool(code_type.get('enabled'))
            var = tk.BooleanVar(value=enabled)
            cb = self.create_checkbox(self.code_types_container, type_name, var)
            cb.configure(command=lambda tn=type_name, v=var: self.on_toggle_code_type(tn, v))
            cb.pack(anchor="w", pady=2)
            self._code_type_vars[type_name] = var

    def on_toggle_code_type(self, type_name: str, var: tk.BooleanVar):
        """Handle toggle of a code protection type and persist change."""
        new_value = bool(var.get())
        success = self.config_service.update_code_protection_type(type_name, new_value)
        if not success:
            # Revert UI state if failed
            var.set(not new_value)
            messagebox.showerror("Error", f"Failed to update '{type_name}'.")

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
            # Convert selected text back to numeric value
            selected_email_text = self.email_mask_type_var.get()
            email_mask_index = self.email_mask_options.index(selected_email_text) if selected_email_text in self.email_mask_options else 0
            self.config_service.email_mask_type = self.email_mask_values[email_mask_index]
            self.config_service.email_defined_text = self.email_defined_text_var.get()
            
            # Phone settings
            self.config_service.phone_enabled = self.phone_enabled_var.get()
            # Convert selected text back to numeric value
            selected_phone_text = self.phone_mask_type_var.get()
            phone_mask_index = self.phone_mask_options.index(selected_phone_text) if selected_phone_text in self.phone_mask_options else 0
            self.config_service.phone_mask_type = self.phone_mask_values[phone_mask_index]
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

    def show_tooltip_info(self, widget, text):
        tk.messagebox.showinfo("Info", text)
    
    def show_menu(self):
        """Show a native dropdown menu under the Menu button"""
        try:
            menu = tk.Menu(self.frame, tearoff=0)
            menu.add_command(label="History", command=self.open_history)
            menu.add_command(label="Save Settings", command=self.save_settings)
            menu.add_separator()
            menu.add_command(label="Exit", command=self.close_application)

            btn = getattr(self, 'menu_btn', None)
            if btn is None:
                x = self.frame.winfo_rootx() + 10
                y = self.frame.winfo_rooty() + 35
            else:
                x = btn.winfo_rootx()
                y = btn.winfo_rooty() + btn.winfo_height()

            menu.tk_popup(x, y)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

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

    def on_email_mask_type_changed(self, selected_value):
        """Handle email mask type selection change"""
        if selected_value == "Defined Text":
            # Pack the email defined text frame right after the email combobox
            self.email_defined_text_frame.pack(fill="x", pady=2, after=self.email_combobox_frame)
        else:
            self.email_defined_text_frame.pack_forget()

    def on_phone_mask_type_changed(self, selected_value):
        """Handle phone mask type selection change"""
        if selected_value == "Defined Text":
            # Pack the phone defined text frame right after the phone combobox
            self.phone_defined_text_frame.pack(fill="x", pady=2, after=self.phone_combobox_frame)
        else:
            self.phone_defined_text_frame.pack_forget()

    def save_masking_settings(self):
        """Save masking settings to database"""
        try:
            # Email settings
            self.config_service.email_enabled = self.email_enabled_var.get()
            # Convert selected text back to numeric value
            selected_email_text = self.email_mask_type_var.get()
            email_mask_index = self.email_mask_options.index(selected_email_text) if selected_email_text in self.email_mask_options else 0
            self.config_service.email_mask_type = self.email_mask_values[email_mask_index]
            self.config_service.email_defined_text = self.email_defined_text_var.get()
            
            # Phone settings
            self.config_service.phone_enabled = self.phone_enabled_var.get()
            # Convert selected text back to numeric value
            selected_phone_text = self.phone_mask_type_var.get()
            phone_mask_index = self.phone_mask_options.index(selected_phone_text) if selected_phone_text in self.phone_mask_options else 0
            self.config_service.phone_mask_type = self.phone_mask_values[phone_mask_index]
            self.config_service.phone_defined_text = self.phone_defined_text_var.get()
            
            # Minimum character lengths
            self.config_service.min_char_lenght_ai = int(self.min_char_ai_var.get())
            self.config_service.min_char_lenght_code = int(self.min_char_code_var.get())
            self.config_service.min_char_lenght_custom_regex = int(self.min_char_regex_var.get())
            
            # Save to database
            self.config_service.save_config_to_database()
            
            messagebox.showinfo("Success", "Masking settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save masking settings: {str(e)}")

    def on_toggle_regex_enabled(self, pattern_id: int, var: tk.BooleanVar):
        """Handle toggle of regex pattern enabled flag and persist change."""
        new_value = bool(var.get())
        success = self.config_service.update_custom_regex_pattern(pattern_id, enabled=new_value)
        if not success:
            # Revert UI state if failed
            var.set(not new_value)
            messagebox.showerror("Error", f"Failed to update regex pattern enabled flag.")

    def on_toggle_regex_priority(self, pattern_id: int, var: tk.BooleanVar):
        """Handle toggle of regex pattern priority flag and persist change."""
        new_value = bool(var.get())
        success = self.config_service.update_custom_regex_pattern(pattern_id, first_priority=new_value)
        if not success:
            # Revert UI state if failed
            var.set(not new_value)
            messagebox.showerror("Error", f"Failed to update regex pattern priority flag.")

    def toggle_add_regex_form(self):
        """Toggle the inline add regex form visibility"""
        if self.regex_form_container.winfo_viewable():
            self.hide_add_regex_form()
        else:
            self.show_add_regex_form()

    def show_add_regex_form(self):
        """Show the inline add regex form"""
        self.regex_form_container.pack(fill="x", pady=(0, 5))
        self.add_new_btn.configure(text="Cancel Add")

    def hide_add_regex_form(self):
        """Hide the inline add regex form and clear fields"""
        self.regex_form_container.pack_forget()
        self.add_new_btn.configure(text="Add New Pattern")
        # Clear form fields
        self.regex_entry.delete(0, "end")
        self.replacement_entry.delete(0, "end")
        self.apply_for_entry.delete(0, "end")
        self.regex_enabled_var.set(True)
        self.regex_priority_var.set(False)

    def save_new_regex_pattern_inline(self):
        """Save new regex pattern from inline form"""
        try:
            regex = self.regex_entry.get().strip()
            replacement = self.replacement_entry.get().strip()
            apply_for = self.apply_for_entry.get().strip()
            enabled = self.regex_enabled_var.get()
            priority = self.regex_priority_var.get()
            
            if not regex:
                messagebox.showerror("Error", "Regex pattern is required!")
                return
            
            if not replacement:
                messagebox.showerror("Error", "Replacement text is required!")
                return
            
            if not apply_for:
                messagebox.showerror("Error", "Apply For field is required!")
                return
            
            # Add to database
            pattern_id = self.config_service.config_repository.add_custom_regex_pattern(
                regex, replacement, apply_for, priority, enabled
            )
            
            if pattern_id:
                # Refresh the patterns list
                self.config_service.load_config_from_database()
                self.load_custom_regex_patterns()
                
                messagebox.showinfo("Success", "Regex pattern added successfully!")
                self.hide_add_regex_form()
            else:
                messagebox.showerror("Error", "Failed to add regex pattern!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save regex pattern: {str(e)}") 