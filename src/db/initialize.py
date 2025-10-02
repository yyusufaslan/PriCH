from src.db.connection import DBConnection
from src.db.clipboard_repository import ClipboardRepository
from src.db.config_repository import ConfigRepository

# Default data definitions
DEFAULT_AI_PROCESSING_TYPES = [
    (0, "Person, including fictional", "Person", True),
    (1, "Companies, agencies, institutions, etc.", "Organization", True),
    (2, "Countries, cities, states", "Location", True),
    (3, "Absolute or relative dates or periods", "Date", True),
    (4, "Non-GPE locations, mountain ranges, bodies of water", "Non-GPE locations", True),
    (5, "Objects, vehicles, foods, etc. (Not services.)", "Product", True),
    (6, "Named hurricanes, battles, wars, sports events, etc.", "Event", True),
    (7, "Titles of books, songs, etc.", "Work of Art", True),
    (8, "Named documents made into laws", "Law", True),
    (9, "Any named language", "Language", True),
    (10, "Times smaller than a day", "Time", True),
    (11, "Percentage, including %", "Percent", True),
    (12, "Monetary values, including unit", "Money", True),
    (13, "Measurements, as of weight or distance", "Quantity", True),
    (14, "first, second, third, etc.", "Ordinal", True),
    (15, "Numerals that do not fall under another type", "Cardinal", True),
    (16, "Nationality, Religious, Political Group", "Nationality, Religious, Political Group", True),
    (17, "Building, Airport, Highway, Bridge, etc.", "Facility", True),
]

DEFAULT_TRUSTED_PROGRAMS = [
    ("Mozilla Firefox (x64 en-US)", True, False),
    ("Obsidian", True, False),
]

DEFAULT_CODE_PROTECTION_TYPES = [
    ("METHOD_NAME", True),
    ("PARAMETER_NAMES", False),
    ("PARAMETER_TYPES", True),
    ("RETURN_TYPE", True),
]

DEFAULT_CUSTOM_REGEX_PATTERNS = [
    ("^[A-Z]+$", "CAPITAL", "AI", True, True),
]

DEFAULT_SPACY_MODELS = [
    ("en", "en_core_web_sm", "resources/python-embed/amd64/Lib/site-packages/en_core_web_sm/__pycache__", "en_core_web_sm", "English (Small)", "12 MB", True, True),
    ("en", "en_core_web_md", "resources/python-embed/amd64/Lib/site-packages/en_core_web_md/__pycache__", "en_core_web_md", "English (Medium)", "31 MB", False, False),
    ("en", "en_core_web_lg", "resources/python-embed/amd64/Lib/site-packages/en_core_web_lg/__pycache__", "en_core_web_lg", "English (Large)", "382 MB", False, False),
]

DEFAULT_TREE_SITTER_LANGUAGES = [
    ("C", "c", "https://github.com/tree-sitter/tree-sitter-c", "resources/tree-sitter-c", True, True),
    ("C++", "cpp", "https://github.com/tree-sitter/tree-sitter-cpp", "resources/tree-sitter-cpp", True, True),
    ("Python", "python", "https://github.com/tree-sitter/tree-sitter-python", "resources/tree-sitter-python", True, True),
    ("JavaScript", "javascript", "https://github.com/tree-sitter/tree-sitter-javascript", "resources/tree-sitter-javascript", True, True),
    ("Java", "java", "https://github.com/tree-sitter/tree-sitter-java", "resources/tree-sitter-java", True, False),
]

DEFAULT_CATEGORIES = [
    "Personal",
    "Work",
    "Code",
    "Sensitive",
    "Temporary",
    "Important",
    "Finance",
    "Health",
    "Education",
    "Entertainment",
]

def initialize_database():
    db = DBConnection()
    repo = ClipboardRepository()
    config_repo = ConfigRepository()
    
    # Always initialize schema first
    print("Initializing database schema...")
    db.initialize_schema()
    
    # Check if settings table has any data
    config = config_repo.get_config()
    if config is None:
        print("Inserting default settings...")
        # Insert default settings
        conn = db.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO config (
                ai_enabled, darkMode, showAllMaskedTexts, unMaskManual, 
                trusted_programs_enabled, email_enabled, email_mask_type, phone_enabled, phone_mask_type, 
                code_protection_enabled, email_defined_text, phone_defined_text, 
                custom_regex_enabled, min_char_lenght_code, min_char_lenght_ai, 
                min_char_lenght_custom_regex, custom_regex_first_priority_for_ai, 
                custom_regex_first_priority_for_code, show_progress_bar, 
                progress_bar_time_minutes_for_short_model, 
                progress_bar_time_minutes_for_medium_model, 
                progress_bar_time_minutes_for_long_model, 
                disable_all_features, disable_masking
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (False, False, False, False, False, False, 0, False, 0, False, '', '', False, 20, 15, 20, False, False, False, 1, 2, 3, False, False))
        conn.commit()
        cur.close()

    # AI Processing Types
    if not config_repo.get_ai_processing_types():
        print("Inserting AI processing types...")
        for ai_mask_option, desc, short_desc, enabled in DEFAULT_AI_PROCESSING_TYPES:
            config_repo.add_ai_processing_type(ai_mask_option, desc, short_desc, enabled)

    # Trusted Programs
    if not config_repo.get_trusted_programs():
        print("Inserting trusted programs...")
        for program_name, enabled, deleted in DEFAULT_TRUSTED_PROGRAMS:
            config_repo.add_trusted_program(program_name, enabled, deleted)

    # Code Protection Types
    if not config_repo.get_code_protection_types():
        print("Inserting code protection types...")
        for type_name, enabled in DEFAULT_CODE_PROTECTION_TYPES:
            config_repo.add_code_protection_type(type_name, enabled)

    # Custom Regex Patterns
    if not config_repo.get_custom_regex_patterns():
        print("Inserting custom regex patterns...")
        for regex, replacement, apply_for, first_priority, enabled in DEFAULT_CUSTOM_REGEX_PATTERNS:
            config_repo.add_custom_regex_pattern(regex, replacement, apply_for, first_priority, enabled)

    # SpaCy Models
    if not config_repo.get_spacy_models():
        print("Inserting SpaCy models...")
        for lang, name, path, short_name, desc, size, enabled, downloaded in DEFAULT_SPACY_MODELS:
            config_repo.add_spacy_model(lang, name, path, short_name, desc, size, enabled, downloaded)

    # Tree Sitter Languages
    if not config_repo.get_tree_sitter_languages():
        print("Inserting Tree Sitter languages...")
        for lang_name, lib_name, remote_path, local_path, enabled, downloaded in DEFAULT_TREE_SITTER_LANGUAGES:
            config_repo.add_tree_sitter_language(lang_name, lib_name, remote_path, local_path, enabled, downloaded)

    # Categories
    if not repo.get_categories():
        print("Inserting default categories...")
        for category_name in DEFAULT_CATEGORIES:
            repo.add_category(category_name)
    
    print("Database initialized successfully with default data.") 