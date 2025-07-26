import tkinter as tk
from tkinter import ttk, messagebox

class HistoryPage:
    def __init__(self, parent, clipboard_service):
        self.frame = tk.Frame(parent)
        self.clipboard_service = clipboard_service
        self.auto_refresh_enabled = True
        self.auto_refresh_id = None
        
        # Create main container
        main_container = tk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="Clipboard History", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_container)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Refresh button
        self.refresh_btn = tk.Button(buttons_frame, text="Refresh", command=self.refresh_history)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear history button
        self.clear_btn = tk.Button(buttons_frame, text="Clear History", command=self.clear_history)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-refresh toggle button
        self.auto_refresh_btn = tk.Button(buttons_frame, text="Auto-Refresh: ON", 
                                        command=self.toggle_auto_refresh, bg="lightgreen")
        self.auto_refresh_btn.pack(side=tk.LEFT)
        
        # Create treeview for history
        self.create_history_treeview(main_container)
        
        # Status label
        self.status_label = tk.Label(main_container, text="Ready", fg="gray")
        self.status_label.pack(pady=(10, 0))
        
        # Initial load
        self.refresh_history()
        
        # Start auto-refresh
        self.start_auto_refresh()

    def create_history_treeview(self, parent):
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("Time", "Original Text", "Masked Text", "Source Process")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("Time", text="Time")
        self.tree.heading("Original Text", text="Original Text")
        self.tree.heading("Masked Text", text="Masked Text")
        self.tree.heading("Source Process", text="Source Process")
        
        # Column widths
        self.tree.column("Time", width=150)
        self.tree.column("Original Text", width=300)
        self.tree.column("Masked Text", width=300)
        self.tree.column("Source Process", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def start_auto_refresh(self):
        """Start the auto-refresh timer"""
        if self.auto_refresh_enabled:
            self.refresh_history()
            # Schedule next refresh in 2 seconds
            self.auto_refresh_id = self.frame.after(1000, self.start_auto_refresh)

    def stop_auto_refresh(self):
        """Stop the auto-refresh timer"""
        if self.auto_refresh_id:
            self.frame.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None

    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        if self.auto_refresh_enabled:
            self.auto_refresh_btn.config(text="Auto-Refresh: ON", bg="lightgreen")
            self.start_auto_refresh()
        else:
            self.auto_refresh_btn.config(text="Auto-Refresh: OFF", bg="lightcoral")
            self.stop_auto_refresh()

    def refresh_history(self):
        """Refresh the history list"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get history from service
            history = self.clipboard_service.get_history(limit=100)
            
            # Add items to treeview
            for entry in history:
                # Handle both dictionary and tuple formats for backward compatibility
                if isinstance(entry, dict):
                    # New dictionary format
                    original_text = entry.get('originalText', '')
                    masked_text = entry.get('maskedText', '')
                    source_process = entry.get('sourceProcess', '')
                    timestamp = entry.get('timestamp', '')
                    created_at = entry.get('createdAt', '')
                else:
                    # Old tuple format (fallback)
                    original_text = entry[1] if len(entry) > 1 else ''
                    masked_text = entry[2] if len(entry) > 2 else ''
                    source_process = entry[3] if len(entry) > 3 else ''
                    timestamp = entry[4] if len(entry) > 4 else ''
                    created_at = entry[5] if len(entry) > 5 else ''
                
                # Truncate text for display
                display_original = original_text[:50] + "..." if len(original_text) > 50 else original_text
                display_masked = masked_text[:50] + "..." if len(masked_text) > 50 else masked_text
                
                # Insert into treeview
                item = self.tree.insert("", "end", values=(
                    timestamp,
                    display_original,
                    display_masked,
                    source_process
                ))
                
                # Store full text in tags for double-click access
                self.tree.item(item, tags=(original_text, masked_text))
            
            self.status_label.config(text=f"History refreshed - {len(history)} items")
            
        except Exception as e:
            print(f"Error refreshing history: {e}")
            self.status_label.config(text="Error refreshing history")

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all clipboard history?"):
            try:
                self.clipboard_service.db.clear_history()
                self.refresh_history()
                self.status_label.config(text="History cleared")
            except Exception as e:
                self.status_label.config(text=f"Error clearing history: {str(e)}")
                print(f"Error clearing history: {e}")

    def on_item_double_click(self, event):
        """Handle double-click on history item"""
        item = self.tree.selection()[0]
        tags = self.tree.item(item, "tags")
        if tags:
            original_text, masked_text = tags
            self.show_item_details(original_text, masked_text, item)

    def show_item_details(self, original_text, masked_text, item_id):
        """Show detailed view of clipboard item with mask mappings"""
        # Get the full history data for this item
        history_data = None
        history_list = self.clipboard_service.get_history(limit=100)  # Get more items to find the one we need
        
        # Find the item by matching the text
        for entry in history_list:
            if entry.get('originalText') == original_text and entry.get('maskedText') == masked_text:
                history_data = entry
                break
        
        if not history_data:
            # Fallback to basic display
            self.show_basic_item_details(original_text, masked_text)
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.frame)
        detail_window.title("Clipboard Item Details")
        detail_window.geometry("800x600")
        detail_window.resizable(True, True)
        
        # Create main frame with scrollbar
        main_frame = tk.Frame(detail_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = tk.Label(scrollable_frame, text="Clipboard Item Details", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Source Process
        source_frame = tk.LabelFrame(scrollable_frame, text="Source Process", padx=10, pady=5)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        source_label = tk.Label(source_frame, text=history_data.get('sourceProcess', 'Unknown'), font=("Arial", 10))
        source_label.pack(anchor="w")
        
        # Timestamp
        timestamp_frame = tk.LabelFrame(scrollable_frame, text="Timestamp", padx=10, pady=5)
        timestamp_frame.pack(fill=tk.X, pady=(0, 10))
        timestamp_label = tk.Label(timestamp_frame, text=history_data.get('timestamp', 'Unknown'), font=("Arial", 10))
        timestamp_label.pack(anchor="w")
        
        # Original Text
        original_frame = tk.LabelFrame(scrollable_frame, text="Original Text", padx=10, pady=5)
        original_frame.pack(fill=tk.X, pady=(0, 10))
        original_text_widget = tk.Text(original_frame, height=4, wrap=tk.WORD)
        original_text_widget.insert("1.0", original_text)
        original_text_widget.config(state=tk.DISABLED)
        original_text_widget.pack(fill=tk.X)
        
        # Copy original button
        copy_original_btn = tk.Button(original_frame, text="Copy Original", 
                                    command=lambda: self.copy_to_clipboard(original_text))
        copy_original_btn.pack(pady=(5, 0))
        
        # Masked Text
        masked_frame = tk.LabelFrame(scrollable_frame, text="Masked Text", padx=10, pady=5)
        masked_frame.pack(fill=tk.X, pady=(0, 10))
        masked_text_widget = tk.Text(masked_frame, height=4, wrap=tk.WORD)
        masked_text_widget.insert("1.0", masked_text)
        masked_text_widget.config(state=tk.DISABLED)
        masked_text_widget.pack(fill=tk.X)
        
        # Copy masked button
        copy_masked_btn = tk.Button(masked_frame, text="Copy Masked", 
                                  command=lambda: self.copy_to_clipboard(masked_text))
        copy_masked_btn.pack(pady=(5, 0))
        
        # Mask Mappings
        mask_mappings = history_data.get('maskMappings', [])
        if mask_mappings:
            mappings_frame = tk.LabelFrame(scrollable_frame, text=f"Mask Mappings ({len(mask_mappings)} items)", padx=10, pady=5)
            mappings_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Create treeview for mappings
            mappings_tree = ttk.Treeview(mappings_frame, columns=("Original", "Masked", "Type", "Priority"), show="headings", height=6)
            mappings_tree.heading("Original", text="Original Text")
            mappings_tree.heading("Masked", text="Masked Text")
            mappings_tree.heading("Type", text="Mask Type")
            mappings_tree.heading("Priority", text="Priority")
            
            # Set column widths
            mappings_tree.column("Original", width=200)
            mappings_tree.column("Masked", width=200)
            mappings_tree.column("Type", width=100)
            mappings_tree.column("Priority", width=80)
            
            # Add mappings to treeview
            for mapping in mask_mappings:
                mappings_tree.insert("", "end", values=(
                    mapping.get('originalText', ''),
                    mapping.get('maskedText', ''),
                    mapping.get('maskType', ''),
                    mapping.get('priority', 0)
                ))
            
            mappings_tree.pack(fill=tk.X)
            
            # Add scrollbar for mappings
            mappings_scrollbar = ttk.Scrollbar(mappings_frame, orient="vertical", command=mappings_tree.yview)
            mappings_tree.configure(yscrollcommand=mappings_scrollbar.set)
            mappings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            mappings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        else:
            # No mappings
            no_mappings_frame = tk.LabelFrame(scrollable_frame, text="Mask Mappings", padx=10, pady=5)
            no_mappings_frame.pack(fill=tk.X, pady=(0, 10))
            no_mappings_label = tk.Label(no_mappings_frame, text="No mask mappings found", font=("Arial", 10, "italic"))
            no_mappings_label.pack()
        
        # Categories (if implemented)
        categories = history_data.get('categories', [])
        if categories:
            categories_frame = tk.LabelFrame(scrollable_frame, text="Categories", padx=10, pady=5)
            categories_frame.pack(fill=tk.X, pady=(0, 10))
            categories_text = ", ".join([cat.get('name', '') for cat in categories])
            categories_label = tk.Label(categories_frame, text=categories_text, font=("Arial", 10))
            categories_label.pack(anchor="w")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_basic_item_details(self, original_text, masked_text):
        """Show basic item details when full history data is not available"""
        detail_window = tk.Toplevel(self.frame)
        detail_window.title("Clipboard Item Details")
        detail_window.geometry("600x400")
        
        # Title
        title_label = tk.Label(detail_window, text="Clipboard Item Details", font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 20))
        
        # Original Text
        original_frame = tk.LabelFrame(detail_window, text="Original Text", padx=10, pady=5)
        original_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        original_text_widget = tk.Text(original_frame, height=4, wrap=tk.WORD)
        original_text_widget.insert("1.0", original_text)
        original_text_widget.config(state=tk.DISABLED)
        original_text_widget.pack(fill=tk.X)
        
        # Copy original button
        copy_original_btn = tk.Button(original_frame, text="Copy Original", 
                                    command=lambda: self.copy_to_clipboard(original_text))
        copy_original_btn.pack(pady=(5, 0))
        
        # Masked Text
        masked_frame = tk.LabelFrame(detail_window, text="Masked Text", padx=10, pady=5)
        masked_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        masked_text_widget = tk.Text(masked_frame, height=4, wrap=tk.WORD)
        masked_text_widget.insert("1.0", masked_text)
        masked_text_widget.config(state=tk.DISABLED)
        masked_text_widget.pack(fill=tk.X)
        
        # Copy masked button
        copy_masked_btn = tk.Button(masked_frame, text="Copy Masked", 
                                  command=lambda: self.copy_to_clipboard(masked_text))
        copy_masked_btn.pack(pady=(5, 0))
        
        # Note about mask mappings
        note_label = tk.Label(detail_window, text="Note: Mask mappings not available for this item", 
                             font=("Arial", 9, "italic"), fg="gray")
        note_label.pack(pady=(20, 0))

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        import pyperclip
        pyperclip.copy(text)
        self.status_label.config(text="Text copied to clipboard")

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
        # Start auto-refresh when page is shown
        if self.auto_refresh_enabled:
            self.start_auto_refresh()

    def hide(self):
        self.frame.pack_forget()
        # Stop auto-refresh when page is hidden
        self.stop_auto_refresh() 