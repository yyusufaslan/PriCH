import platform
import customtkinter as ctk


class ScrollManager:
    """Utility class for managing horizontal mouse wheel scrolling across different platforms"""
    
    @staticmethod
    def bind_horizontal_scroll(widget, target_canvas=None):
        """
        Bind horizontal mouse wheel scrolling to a widget
        
        Args:
            widget: The widget to bind scroll events to
            target_canvas: The canvas to scroll (if None, will auto-detect parent canvas)
        """
        def get_parent_canvas(w):
            """Find the parent canvas with _parent_canvas attribute"""
            current = w
            while current and not hasattr(current, '_parent_canvas'):
                current = current.master
            return current._parent_canvas if current and hasattr(current, '_parent_canvas') else None
        
        # Use provided target_canvas or auto-detect
        canvas = target_canvas or get_parent_canvas(widget)
        if not canvas:
            return
        
        system = platform.system()
        
        if system == "Windows":
            widget.bind("<MouseWheel>", lambda e: canvas.xview_scroll(-1 * (e.delta // 120), "units"))
        elif system == "Darwin":  # macOS
            widget.bind("<MouseWheel>", lambda e: canvas.xview_scroll(-1 * int(e.delta), "units"))
        else:  # Linux
            widget.bind("<Button-4>", lambda e: canvas.xview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: canvas.xview_scroll(1, "units"))

    @staticmethod
    def bind_vertical_scroll(widget, target_canvas=None):
        """
        Bind vertical mouse wheel scrolling to a widget
        
        Args:
            widget: The widget to bind scroll events to
            target_canvas: The canvas to scroll (if None, will auto-detect parent canvas)
        """
        def get_parent_canvas(w):
            """Find the parent canvas with _parent_canvas attribute"""
            current = w
            while current and not hasattr(current, '_parent_canvas'):
                current = current.master
            return current._parent_canvas if current and hasattr(current, '_parent_canvas') else None
        
        # Use provided target_canvas or auto-detect
        canvas = target_canvas or get_parent_canvas(widget)
        if not canvas:
            return
        
        system = platform.system()
        
        if system == "Windows":
            widget.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        elif system == "Darwin":  # macOS
            widget.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * int(e.delta), "units"))
        else:  # Linux
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    @staticmethod
    def create_horizontal_scrollable_frame(parent, **kwargs):
        """
        Create a horizontal scrollable frame with hidden scrollbar and mouse wheel support
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkScrollableFrame
            
        Returns:
            CTkScrollableFrame with hidden scrollbar and mouse wheel support
        """
        # Set default orientation to horizontal if not specified
        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'horizontal'
        
        frame = ctk.CTkScrollableFrame(parent, **kwargs)
        
        # Hide scrollbar completely
        frame._scrollbar.configure(width=0)
        frame._scrollbar.pack_forget()
        
        # Bind mouse wheel for horizontal scrolling
        ScrollManager.bind_horizontal_scroll(frame)
        
        return frame

    @staticmethod
    def create_vertical_scrollable_frame(parent, **kwargs):
        """
        Create a vertical scrollable frame with hidden scrollbar and mouse wheel support
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkScrollableFrame
            
        Returns:
            CTkScrollableFrame with hidden scrollbar and mouse wheel support
        """
        # Set default orientation to vertical if not specified
        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'vertical'
        
        frame = ctk.CTkScrollableFrame(parent, **kwargs)
        
        # Hide scrollbar completely
        frame._scrollbar.configure(width=0)
        frame._scrollbar.pack_forget()
        
        # Bind mouse wheel for vertical scrolling
        ScrollManager.bind_vertical_scroll(frame)
        
        return frame

    @staticmethod
    def bind_scroll_to_widgets(widgets, scroll_type='horizontal', target_canvas=None):
        """
        Bind scroll events to multiple widgets at once
        
        Args:
            widgets: List of widgets to bind scroll events to
            scroll_type: 'horizontal' or 'vertical'
            target_canvas: The canvas to scroll (if None, will auto-detect for each widget)
        """
        for widget in widgets:
            if scroll_type == 'horizontal':
                ScrollManager.bind_horizontal_scroll(widget, target_canvas)
            else:
                ScrollManager.bind_vertical_scroll(widget, target_canvas)

    @staticmethod
    def create_scrollable_cards_container(parent, **kwargs):
        """
        Create a horizontal scrollable container specifically for cards with mouse wheel support
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkScrollableFrame
            
        Returns:
            CTkScrollableFrame configured for cards display
        """
        # Default settings for cards container
        default_kwargs = {
            'orientation': 'horizontal',
            'fg_color': '#1a1a1a'
        }
        default_kwargs.update(kwargs)
        
        frame = ctk.CTkScrollableFrame(parent, **default_kwargs)
        
        # Hide scrollbar completely
        frame._scrollbar.configure(width=0)
        frame._scrollbar.pack_forget()
        
        # Bind mouse wheel for horizontal scrolling
        ScrollManager.bind_horizontal_scroll(frame)
        
        return frame

    @staticmethod
    def create_scrollable_categories_container(parent, **kwargs):
        """
        Create a horizontal scrollable container specifically for categories with mouse wheel support
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for CTkScrollableFrame
            
        Returns:
            CTkScrollableFrame configured for categories display
        """
        # Default settings for categories container
        default_kwargs = {
            'orientation': 'horizontal',
            'height': 40,
            'width': 100,
            'fg_color': '#2d2d2d'
        }
        default_kwargs.update(kwargs)
        
        frame = ctk.CTkScrollableFrame(parent, **default_kwargs)
        
        # Hide scrollbar completely
        frame._scrollbar.configure(width=0)
        frame._scrollbar.pack_forget()
        
        # Bind mouse wheel for horizontal scrolling
        ScrollManager.bind_horizontal_scroll(frame)
        
        return frame
