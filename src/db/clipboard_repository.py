from src.db.connection import DBConnection

class ClipboardRepository:
    def __init__(self):
        self.db = DBConnection()

    # Clipboard History CRUD
    def add_entry(self, original_text, masked_text, source_process, timestamp, mask_mappings=None):
        conn = self.db.connect()
        cur = conn.cursor()
        
        # Insert clipboard history entry
        cur.execute("""
            INSERT INTO clipboard_history (original_text, masked_text, source_process, timestamp)
            VALUES (?, ?, ?, ?)
        """, (original_text, masked_text, source_process, timestamp))
        
        history_id = cur.lastrowid
        
        # Insert mask mappings if provided
        if mask_mappings:
            for i, mapping in enumerate(mask_mappings):
                cur.execute("""
                    INSERT INTO mask_mappings (history_id, original_text, masked_text, mask_type, priority)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    history_id,
                    mapping.get('originalText', ''),
                    mapping.get('maskedText', ''),
                    mapping.get('maskType', ''),
                    i  # Use index as priority
                ))
        
        conn.commit()
        cur.close()
        return history_id

    def get_history(self, limit=100):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, original_text, masked_text, source_process, timestamp, created_at
            FROM clipboard_history 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        result = cur.fetchall()
        cur.close()
        return result

    def get_history_with_mappings(self, limit=100):
        """Get history entries with their mask mappings"""
        conn = self.db.connect()
        cur = conn.cursor()
        
        # Get history entries
        cur.execute("""
            SELECT id, original_text, masked_text, source_process, timestamp, created_at
            FROM clipboard_history 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        history_entries = cur.fetchall()
        
        # Get mask mappings for each entry
        result = []
        for entry in history_entries:
            history_id = entry[0]
            cur.execute("""
                SELECT original_text, masked_text, mask_type, priority
                FROM mask_mappings 
                WHERE history_id = ?
                ORDER BY priority
            """, (history_id,))
            mappings = cur.fetchall()
            
            # Convert to list of dictionaries
            mask_mappings = []
            for mapping in mappings:
                mask_mappings.append({
                    'originalText': mapping[0],
                    'maskedText': mapping[1],
                    'maskType': mapping[2],
                    'priority': mapping[3]
                })
            
            # Add mappings to history entry
            history_dict = {
                'id': entry[0],
                'originalText': entry[1],
                'maskedText': entry[2],
                'sourceProcess': entry[3],
                'timestamp': entry[4],
                'createdAt': entry[5],
                'maskMappings': mask_mappings
            }
            result.append(history_dict)
        
        cur.close()
        return result

    def get_mask_mappings_for_history(self, history_id):
        """Get mask mappings for a specific history entry"""
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT original_text, masked_text, mask_type, priority
            FROM mask_mappings 
            WHERE history_id = ?
            ORDER BY priority
        """, (history_id,))
        result = cur.fetchall()
        cur.close()
        
        mappings = []
        for row in result:
            mappings.append({
                'originalText': row[0],
                'maskedText': row[1],
                'maskType': row[2],
                'priority': row[3]
            })
        return mappings

    def clear_history(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM clipboard_history")
        conn.commit()
        cur.close()

    # Categories CRUD
    def add_category(self, name):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        cur.close()

    def get_categories(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        result = cur.fetchall()
        cur.close()
        return result

    def delete_category(self, category_id):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        cur.close()

    # History-Categories relationship CRUD
    def add_history_category(self, history_id, category_id):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO history_categories (history_id, category_id)
            VALUES (?, ?)
        """, (history_id, category_id))
        conn.commit()
        cur.close()

    def remove_history_category(self, history_id, category_id):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM history_categories 
            WHERE history_id = ? AND category_id = ?
        """, (history_id, category_id))
        conn.commit()
        cur.close()

    def get_categories_for_history(self, history_id):
        """Get categories for a specific history entry"""
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.name
            FROM categories c
            JOIN history_categories hc ON c.id = hc.category_id
            WHERE hc.history_id = ?
            ORDER BY c.name
        """, (history_id,))
        result = cur.fetchall()
        cur.close()
        return result

    def get_history_by_category(self, category_id, limit=100):
        """Get history entries for a specific category"""
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT h.id, h.original_text, h.masked_text, h.source_process, h.timestamp, h.created_at
            FROM clipboard_history h
            JOIN history_categories hc ON h.id = hc.history_id
            WHERE hc.category_id = ?
            ORDER BY h.created_at DESC 
            LIMIT ?
        """, (category_id, limit))
        result = cur.fetchall()
        cur.close()
        return result

    # Additional utility methods
    def is_masked_text_in_history(self, masked_text):
        """Check if masked text exists in history"""
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM clipboard_history WHERE masked_text = ?", (masked_text,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0

    def get_original_text(self, masked_text):
        """Get original text for a masked text"""
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT original_text FROM clipboard_history WHERE masked_text = ? LIMIT 1", (masked_text,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None

    