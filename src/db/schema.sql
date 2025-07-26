-- Config table
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY,
    ai_enabled BOOLEAN,
    showAllMaskedTexts BOOLEAN,
    darkMode BOOLEAN,
    unMaskManual BOOLEAN,
    trusted_programs_enabled BOOLEAN,
    email_enabled BOOLEAN,
    email_mask_type INTEGER,
    phone_enabled BOOLEAN,
    phone_mask_type INTEGER,
    code_protection_enabled BOOLEAN,
    email_defined_text TEXT,
    phone_defined_text TEXT,
    custom_regex_enabled BOOLEAN,
    min_char_lenght_code INTEGER,
    min_char_lenght_ai INTEGER,
    min_char_lenght_custom_regex INTEGER,
    custom_regex_first_priority_for_ai BOOLEAN,
    custom_regex_first_priority_for_code BOOLEAN,
    show_progress_bar BOOLEAN,
    progress_bar_time_minutes_for_short_model INTEGER,
    progress_bar_time_minutes_for_medium_model INTEGER,
    progress_bar_time_minutes_for_long_model INTEGER,
    disable_all_features BOOLEAN,
    disable_masking BOOLEAN
);

-- AI Processing Types table
CREATE TABLE IF NOT EXISTS ai_processing_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_mask_option INTEGER UNIQUE,
    ai_mask_option_description TEXT,
    ai_mask_option_short_description TEXT,
    enabled BOOLEAN
);

-- Trusted Programs table
CREATE TABLE IF NOT EXISTS trusted_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_name TEXT UNIQUE,
    enabled BOOLEAN,
    deleted BOOLEAN
);

-- Code Protection Types table
CREATE TABLE IF NOT EXISTS code_protection_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT UNIQUE,
    enabled BOOLEAN
);

-- Custom Regex Patterns table
CREATE TABLE IF NOT EXISTS custom_regex_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regex TEXT UNIQUE,
    replacement TEXT,
    apply_for TEXT,
    first_priority BOOLEAN,
    enabled BOOLEAN
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Clipboard history table
CREATE TABLE IF NOT EXISTS clipboard_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_text TEXT NOT NULL,
    masked_text TEXT NOT NULL,
    source_process TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Junction table for history-categories many-to-many relationship
CREATE TABLE IF NOT EXISTS history_categories (
    history_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (history_id, category_id),
    FOREIGN KEY (history_id) REFERENCES clipboard_history(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Mask mappings table
CREATE TABLE IF NOT EXISTS mask_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    history_id INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    masked_text TEXT NOT NULL,
    mask_type TEXT NOT NULL, -- e.g., 'PERSON', 'ORG', 'EMAIL', etc.
    priority INTEGER NOT NULL,
    FOREIGN KEY (history_id) REFERENCES clipboard_history(id) ON DELETE CASCADE
);

-- Spacy models table
CREATE TABLE IF NOT EXISTS spacy_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_language TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_path TEXT NOT NULL,
    model_short_name TEXT NOT NULL,
    model_description TEXT NOT NULL,
    model_size TEXT NOT NULL,
    enabled BOOLEAN,
    downloaded BOOLEAN
);

-- Custom Terms table
CREATE TABLE IF NOT EXISTS custom_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    replacement TEXT NOT NULL,
    spacy_model_id INTEGER NOT NULL,
    enabled BOOLEAN
);

-- Tree Sitter Languages table
CREATE TABLE IF NOT EXISTS tree_sitter_languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_name TEXT NOT NULL,
    language_library_name TEXT NOT NULL,
    language_remote_path TEXT NOT NULL,
    language_local_path TEXT NOT NULL,
    enabled BOOLEAN,
    downloaded BOOLEAN
); 