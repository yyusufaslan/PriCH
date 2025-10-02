from src.db.connection import DBConnection

class ConfigRepository:
    def __init__(self):
        self.db = DBConnection()

    # Settings CRUD
    def get_settings(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM config LIMIT 1")
        result = cur.fetchone()
        cur.close()
        return result

    def update_settings(self, **kwargs):
        conn = self.db.connect()
        cur = conn.cursor()
        
        # Build the SET clause dynamically
        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values())
        
        cur.execute(f"UPDATE config SET {set_clause} WHERE id = 1", values)
        conn.commit()
        cur.close()

    # Config CRUD
    def get_config(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM config LIMIT 1")
        result = cur.fetchone()
        cur.close()
        return result

    def update_config(self, **kwargs):
        conn = self.db.connect()
        cur = conn.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values())
        cur.execute(f"UPDATE config SET {set_clause} WHERE id = 1", values)
        conn.commit()
        cur.close()
    
    # AI Processing Types CRUD
    def add_ai_processing_type(self, ai_mask_option, description, short_description, enabled):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO ai_processing_types (ai_mask_option, ai_mask_option_description, ai_mask_option_short_description, enabled) VALUES (?, ?, ?, ?)",
            (ai_mask_option, description, short_description, enabled)
        )
        conn.commit()
        cur.execute("SELECT id FROM ai_processing_types WHERE ai_mask_option = ?", (ai_mask_option,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None

    def get_ai_processing_types(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ai_processing_types")
        result = cur.fetchall()
        cur.close()
        return result
    
    def update_ai_processing_type(self, ai_mask_option, enabled=None):
        conn = self.db.connect()
        cur = conn.cursor()
        set_parts = []
        values = []
        if enabled is not None:
            set_parts.append("enabled = ?")
            values.append(enabled)
        if not set_parts:
            cur.close()
            return False
        set_clause = ', '.join(set_parts)
        values.append(ai_mask_option)
        cur.execute(f"UPDATE ai_processing_types SET {set_clause} WHERE ai_mask_option = ?", values)
        conn.commit()
        cur.close()
        return True
    
    # Trusted Programs CRUD
    def add_trusted_program(self, program_name, enabled, deleted):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO trusted_programs (program_name, enabled, deleted) VALUES (?, ?, ?)",
            (program_name, enabled, deleted)
        )
        conn.commit()
        cur.execute("SELECT id FROM trusted_programs WHERE program_name = ?", (program_name,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None

    def get_trusted_programs(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM trusted_programs")
        result = cur.fetchall()
        cur.close()
        return result

    def update_trusted_program(self, program_name, enabled=None, deleted=None):
        conn = self.db.connect()
        cur = conn.cursor()
        set_parts = []
        values = []
        if enabled is not None:
            set_parts.append("enabled = ?")
            values.append(enabled)
        if deleted is not None:
            set_parts.append("deleted = ?")
            values.append(deleted)
        if not set_parts:
            cur.close()
            return False
        set_clause = ', '.join(set_parts)
        values.append(program_name)
        cur.execute(f"UPDATE trusted_programs SET {set_clause} WHERE program_name = ?", values)
        conn.commit()
        cur.close()
        return True

    # Code Protection Types CRUD
    def add_code_protection_type(self, type_name, enabled):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO code_protection_types (type_name, enabled) VALUES (?, ?)",
            (type_name, enabled)
        )
        conn.commit()
        cur.execute("SELECT id FROM code_protection_types WHERE type_name = ?", (type_name,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None

    def get_code_protection_types(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM code_protection_types")
        result = cur.fetchall()
        cur.close()
        return result
    
    def update_code_protection_type(self, type_name, enabled):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("UPDATE code_protection_types SET enabled = ? WHERE type_name = ?", (enabled, type_name))
        conn.commit()
        cur.close()
        return True
    
    def delete_code_protection_type(self, type_name):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM code_protection_types WHERE type_name = ?", (type_name,))
        conn.commit()
        cur.close()
        return True
    
    # Custom Regex Patterns CRUD
    def add_custom_regex_pattern(self, regex, replacement, apply_for, first_priority, enabled):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO custom_regex_patterns (regex, replacement, apply_for, first_priority, enabled) VALUES (?, ?, ?, ?, ?)",
            (regex, replacement, apply_for, first_priority, enabled)
        )
        conn.commit()
        cur.execute("SELECT id FROM custom_regex_patterns WHERE regex = ?", (regex,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None

    def get_custom_regex_patterns(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM custom_regex_patterns")
        result = cur.fetchall()
        cur.close()
        return result
    
    def update_custom_regex_pattern(self, pattern_id, enabled=None, first_priority=None):
        conn = self.db.connect()
        cur = conn.cursor()
        set_parts = []
        values = []
        if enabled is not None:
            set_parts.append("enabled = ?")
            values.append(enabled)
        if first_priority is not None:
            set_parts.append("first_priority = ?")
            values.append(first_priority)
        if not set_parts:
            cur.close()
            return False
        set_clause = ', '.join(set_parts)
        values.append(pattern_id)
        cur.execute(f"UPDATE custom_regex_patterns SET {set_clause} WHERE id = ?", values)
        conn.commit()
        cur.close()
        return True
    
    # Spacy Models CRUD
    def add_spacy_model(self, model_language, model_name, model_path, model_short_name, model_description, model_size, enabled, downloaded):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO spacy_models (model_language, model_name, model_path, model_short_name, model_description, model_size, enabled, downloaded) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (model_language, model_name, model_path, model_short_name, model_description, model_size, enabled, downloaded)
        )
        conn.commit()
        result = cur.lastrowid
        cur.close()
        return result

    def get_spacy_models(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM spacy_models")
        result = cur.fetchall()
        cur.close()
        return result

    # Custom Terms CRUD
    def add_custom_term(self, term, replacement, spacy_model_id, enabled):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO custom_terms (term, replacement, spacy_model_id, enabled) VALUES (?, ?, ?, ?)",
            (term, replacement, spacy_model_id, enabled)
        )
        conn.commit()
        result = cur.lastrowid
        cur.close()
        return result

    def get_custom_terms(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM custom_terms")
        result = cur.fetchall()
        cur.close()
        return result

    # Tree Sitter Languages CRUD
    def add_tree_sitter_language(self, language_name, language_library_name, language_remote_path, language_local_path, enabled, downloaded):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tree_sitter_languages (language_name, language_library_name, language_remote_path, language_local_path, enabled, downloaded) VALUES (?, ?, ?, ?, ?, ?)",
            (language_name, language_library_name, language_remote_path, language_local_path, enabled, downloaded)
        )
        conn.commit()
        result = cur.lastrowid
        cur.close()
        return result

    def get_tree_sitter_languages(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tree_sitter_languages")
        result = cur.fetchall()
        cur.close()
        return result 