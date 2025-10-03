import os
import platform
from src.db.config_repository import ConfigRepository
from src.utils.platform_utils import PlatformUtils

class ConfigService:
    def __init__(self):
        # Initialize with default values - using database field names exactly
        self.ai_enabled = True
        self.showAllMaskedTexts = False
        self.darkMode = False
        self.unMaskManual = False
        self.trusted_programs_enabled = True
        self.email_enabled = True
        self.email_mask_type = 3
        self.phone_enabled = True
        self.phone_mask_type = 3
        self.code_protection_enabled = True
        self.email_defined_text = ""
        self.phone_defined_text = ""
        self.custom_regex_enabled = True
        self.min_char_lenght_code = 20
        self.min_char_lenght_ai = 15
        self.min_char_lenght_custom_regex = 20
        self.custom_regex_first_priority_for_ai = False
        self.custom_regex_first_priority_for_code = False
        self.show_progress_bar = True
        self.progress_bar_time_minutes_for_short_model = 1
        self.progress_bar_time_minutes_for_medium_model = 2
        self.progress_bar_time_minutes_for_long_model = 3
        self.disable_all_features = False
        self.disable_masking = False
        
        # Additional properties for convenience (not in database)
        self.database_name = platform.system().lower()
        self.trustedPrograms = []  # List of trusted programs from database
        self.customRegexPatterns = []
        self.codeProtectionTypes = []
        self.aiProcessingTypes = []
        self.spacyModels = []
        self.customTerms = []
        self.treeSitterLanguages = []
        
        # SQLite database path (relative to project root)
        self.DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'clipboard_settings.db') 
        self.config_repository = ConfigRepository()
        self.platform_utils = PlatformUtils()

        # Config for dev env
        self.debugMode = False

    def load_config_from_database(self):
        """Load configuration from database into memory"""
        try:
            # Load settings
            settings = self.config_repository.get_settings()
            if settings:
                self._load_settings_from_tuple(settings)
            
            # Load AI processing types
            ai_types = self.config_repository.get_ai_processing_types()
            if ai_types:
                self.aiProcessingTypes = self._convert_ai_types_to_dict(ai_types)
            
            # Load trusted programs
            trusted_programs = self.config_repository.get_trusted_programs()
            if trusted_programs:
                self.trustedPrograms = self._convert_trusted_programs_to_dict(trusted_programs)
            
            # Load code protection types
            code_types = self.config_repository.get_code_protection_types()
            if code_types:
                self.codeProtectionTypes = self._convert_code_types_to_dict(code_types)
            
            # Load custom regex patterns
            regex_patterns = self.config_repository.get_custom_regex_patterns()
            if regex_patterns:
                self.customRegexPatterns = self._convert_regex_patterns_to_dict(regex_patterns)
            
            # Load SpaCy models
            spacy_models = self.config_repository.get_spacy_models()
            if spacy_models:
                self.spacyModels = self._convert_spacy_models_to_dict(spacy_models)
            
            # Load custom terms
            custom_terms = self.config_repository.get_custom_terms()
            if custom_terms:
                self.customTerms = self._convert_custom_terms_to_dict(custom_terms)
            
            # Load tree sitter languages
            tree_languages = self.config_repository.get_tree_sitter_languages()
            if tree_languages:
                self.treeSitterLanguages = self._convert_tree_languages_to_dict(tree_languages)
                
            print("Configuration loaded from database successfully")
            
        except Exception as e:
            print(f"Error loading config from database: {e}")
            # Keep default values if loading fails

    def _load_settings_from_tuple(self, settings_tuple):
        """Load settings from database tuple into memory"""
        if len(settings_tuple) >= 26:
            self.ai_enabled = settings_tuple[1] or False
            self.showAllMaskedTexts = settings_tuple[2] or False
            self.darkMode = settings_tuple[3] or False
            self.unMaskManual = settings_tuple[4] or False
            self.trusted_programs_enabled = settings_tuple[5] or False
            self.email_enabled = settings_tuple[6] or False
            self.email_mask_type = settings_tuple[7] or 0
            self.phone_enabled = settings_tuple[8] or False
            self.phone_mask_type = settings_tuple[9] or 0
            self.code_protection_enabled = settings_tuple[10] or False
            self.email_defined_text = settings_tuple[11] or ""
            self.phone_defined_text = settings_tuple[12] or ""
            self.custom_regex_enabled = settings_tuple[13] or False
            self.min_char_lenght_code = settings_tuple[14] or 20
            self.min_char_lenght_ai = settings_tuple[15] or 15
            self.min_char_lenght_custom_regex = settings_tuple[16] or 20
            self.custom_regex_first_priority_for_ai = settings_tuple[17] or False
            self.custom_regex_first_priority_for_code = settings_tuple[18] or False
            self.show_progress_bar = settings_tuple[19] or False
            self.progress_bar_time_minutes_for_short_model = settings_tuple[20] or 1
            self.progress_bar_time_minutes_for_medium_model = settings_tuple[21] or 2
            self.progress_bar_time_minutes_for_long_model = settings_tuple[22] or 3
            self.disable_all_features = settings_tuple[23] or False
            self.disable_masking = settings_tuple[24] or False

    def save_config_to_database(self):
        """Save current configuration from memory to database"""
        try:
            # Update settings
            self.config_repository.update_settings(
                ai_enabled=self.ai_enabled,
                showAllMaskedTexts=self.showAllMaskedTexts,
                darkMode=self.darkMode,
                unMaskManual=self.unMaskManual,
                trusted_programs_enabled=self.trusted_programs_enabled,
                email_enabled=self.email_enabled,
                email_mask_type=self.email_mask_type,
                phone_enabled=self.phone_enabled,
                phone_mask_type=self.phone_mask_type,
                code_protection_enabled=self.code_protection_enabled,
                email_defined_text=self.email_defined_text,
                phone_defined_text=self.phone_defined_text,
                custom_regex_enabled=self.custom_regex_enabled,
                min_char_lenght_code=self.min_char_lenght_code,
                min_char_lenght_ai=self.min_char_lenght_ai,
                min_char_lenght_custom_regex=self.min_char_lenght_custom_regex,
                custom_regex_first_priority_for_ai=self.custom_regex_first_priority_for_ai,
                custom_regex_first_priority_for_code=self.custom_regex_first_priority_for_code,
                show_progress_bar=self.show_progress_bar,
                progress_bar_time_minutes_for_short_model=self.progress_bar_time_minutes_for_short_model,
                progress_bar_time_minutes_for_medium_model=self.progress_bar_time_minutes_for_medium_model,
                progress_bar_time_minutes_for_long_model=self.progress_bar_time_minutes_for_long_model,
                disable_all_features=self.disable_all_features,
                disable_masking=self.disable_masking
            )
            print("Configuration saved to database successfully")
            
        except Exception as e:
            print(f"Error saving config to database: {e}")

    def update_config_in_database(self, **kwargs):
        """Update specific config values and refresh memory"""
        try:
            # Update in database
            self.config_repository.update_settings(**kwargs)
            
            # Update in memory
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            print("Configuration updated successfully")
            
        except Exception as e:
            print(f"Error updating config: {e}")

    def update_code_protection_type(self, type_name: str, enabled: bool) -> bool:
        """Update a single code protection type's enabled flag in DB and memory."""
        try:
            updated = self.config_repository.update_code_protection_type(type_name, enabled)
            # Reflect change in memory list if present
            for code_type in self.codeProtectionTypes:
                if code_type.get('typeName') == type_name:
                    code_type['enabled'] = enabled
                    break
            return updated
        except Exception as e:
            print(f"Error updating code protection type '{type_name}': {e}")
            return False

    def update_trusted_program(self, program_name: str, enabled: bool = None, deleted: bool = None) -> bool:
        """Update a trusted program flags in DB and memory."""
        try:
            updated = self.config_repository.update_trusted_program(program_name, enabled=enabled, deleted=deleted)
            if not updated:
                return False
            for program in self.trustedPrograms:
                if program.get('programName') == program_name:
                    if enabled is not None:
                        program['enabled'] = enabled
                    if deleted is not None:
                        program['deleted'] = deleted
                    break
            return True
        except Exception as e:
            print(f"Error updating trusted program '{program_name}': {e}")
            return False

    def update_ai_processing_type(self, ai_mask_option: int, enabled: bool) -> bool:
        """Update an AI processing type's enabled flag in DB and memory."""
        try:
            updated = self.config_repository.update_ai_processing_type(ai_mask_option, enabled=enabled)
            if not updated:
                return False
            # Reflect change in memory list if present
            for ai_type in self.aiProcessingTypes:
                if ai_type.get('aiMaskOption') == ai_mask_option:
                    ai_type['enabled'] = enabled
                    break
            return True
        except Exception as e:
            print(f"Error updating AI processing type '{ai_mask_option}': {e}")
            return False

    def update_custom_regex_pattern(self, pattern_id: int, enabled: bool = None, first_priority: bool = None) -> bool:
        """Update a custom regex pattern's flags in DB and memory."""
        try:
            updated = self.config_repository.update_custom_regex_pattern(pattern_id, enabled=enabled, first_priority=first_priority)
            if not updated:
                return False
            # Reflect change in memory list if present
            for pattern in self.customRegexPatterns:
                if pattern.get('id') == pattern_id:
                    if enabled is not None:
                        pattern['enabled'] = enabled
                    if first_priority is not None:
                        pattern['firstPriority'] = first_priority
                    break
            return True
        except Exception as e:
            print(f"Error updating custom regex pattern '{pattern_id}': {e}")
            return False

    def get_config_from_database(self):
        """Get fresh config from database (for debugging)"""
        try:
            self.load_config_from_database()
            return True
        except Exception as e:
            print(f"Error getting config from database: {e}")
            return False

    def update_spacy_model_flags(self, model_short_name: str, enabled: bool | None = None, downloaded: bool | None = None) -> bool:
        """Update spaCy model flags in DB and reflect in-memory list."""
        try:
            updated = self.config_repository.update_spacy_model_flags(model_short_name, enabled=enabled, downloaded=downloaded)
            if not updated:
                return False
            # Update in-memory representation
            for model in self.spacyModels:
                if model.get('modelShortName') == model_short_name:
                    if enabled is not None:
                        model['enabled'] = enabled
                    if downloaded is not None:
                        model['downloaded'] = downloaded
                    break
            return True
        except Exception as e:
            print(f"Error updating spaCy model '{model_short_name}': {e}")
            return False

    # Helper methods for converting database tuples to dictionaries
    def _convert_ai_types_to_dict(self, ai_types):
        return [{'id': t[0], 'aiMaskOption': t[1], 'description': t[2], 'shortDescription': t[3], 'enabled': t[4]} for t in ai_types]

    def _convert_trusted_programs_to_dict(self, trusted_programs):
        return [{'id': t[0], 'programName': t[1], 'enabled': t[2], 'deleted': t[3]} for t in trusted_programs]

    def _convert_code_types_to_dict(self, code_types):
        return [{'id': t[0], 'typeName': t[1], 'enabled': t[2]} for t in code_types]

    def _convert_regex_patterns_to_dict(self, regex_patterns):
        return [{'id': t[0], 'regex': t[1], 'replacement': t[2], 'applyFor': t[3], 'firstPriority': t[4], 'enabled': t[5]} for t in regex_patterns]

    def _convert_spacy_models_to_dict(self, spacy_models):
        return [{'id': t[0], 'modelLanguage': t[1], 'modelName': t[2], 'modelPath': t[3], 'modelShortName': t[4], 'modelDescription': t[5], 'modelSize': t[6], 'enabled': t[7], 'downloaded': t[8]} for t in spacy_models]

    def _convert_custom_terms_to_dict(self, custom_terms):
        return [{'id': t[0], 'term': t[1], 'replacement': t[2], 'spacyModelId': t[3], 'enabled': t[4]} for t in custom_terms]

    def _convert_tree_languages_to_dict(self, tree_languages):
        return [{'id': t[0], 'languageName': t[1], 'languageLibraryName': t[2], 'languageRemotePath': t[3], 'languageLocalPath': t[4], 'enabled': t[5], 'downloaded': t[6]} for t in tree_languages]
    
    def fetch_and_save_installed_apps(self):
        """Fetch all installed apps from system and save to database"""
        try:
            print("Fetching installed applications...")
            installed_apps = self.platform_utils.get_all_installed_programs()
            
            # Save to database as trusted programs (initially disabled)
            for app_name in installed_apps:
                self.config_repository.add_trusted_program(app_name, enabled=True, deleted=False)
            
            print(f"Saved {len(installed_apps)} installed applications to database")
            
            # Update config with trusted programs from database
            self.update_config_trusted_programs()
            
        except Exception as e:
            print(f"Error fetching installed apps: {e}")

    def update_config_trusted_programs(self):
        """Update config with trusted programs from database"""
        try:
            trusted_programs = self.config_repository.get_trusted_programs()
            self.trustedPrograms = []
            
            for program in trusted_programs:
                # Assuming program is a tuple: (id, program_name, enabled, deleted)
                if len(program) >= 4:
                    self.trustedPrograms.append({
                        'id': program[0],
                        'programName': program[1],
                        'enabled': program[2],
                        'deleted': program[3]
                    })
            
            print(f"Updated config with {len(self.trustedPrograms)} trusted programs")
            
        except Exception as e:
            print(f"Error updating config trusted programs: {e}")