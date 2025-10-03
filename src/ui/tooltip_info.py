import tkinter as tk
import customtkinter as ctk

class ToolTipInfo:
    def __init__(self, widget, text, delay_ms=300, pad_x=8, pad_y=4):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.pad_x = pad_x
        self.pad_y = pad_y
        self._after_id = None
        self._tip = None

        # Simple event binding like the working Tooltip class
        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")
        
        # For CustomTkinter widgets, also bind to the underlying canvas
        try:
            if hasattr(self.widget, '_canvas'):
                self.widget._canvas.bind("<Enter>", self._on_enter, add="+")
                self.widget._canvas.bind("<Leave>", self._on_leave, add="+")
                self.widget._canvas.bind("<ButtonPress>", self._on_leave, add="+")
        except:
            pass

    def _on_enter(self, _event=None):
        self._schedule()

    def _on_leave(self, _event=None):
        self._cancel()
        self._hide()

    def _schedule(self):
        self._cancel()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        try:
            if self._tip is not None:
                return
            root = self.widget.winfo_toplevel()
            self._tip = tk.Toplevel(root)
            self._tip.wm_overrideredirect(True)
            self._tip.attributes("-topmost", True)
            self._tip.configure(bg="#333333")

            # Create a frame for better styling
            frame = tk.Frame(
                self._tip,
                background="#333333",
                relief=tk.SOLID,
                borderwidth=1
            )
            frame.pack()

            label = tk.Label(
                frame,
                text=self.text,
                justify=tk.LEFT,
                background="#333333",
                foreground="#ffffff",
                padx=self.pad_x,
                pady=self.pad_y,
                font=("Segoe UI", 9),
                wraplength=300  # Allow text wrapping for long descriptions
            )
            label.pack()

            # Position tooltip near the button
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
            
            # Adjust position if tooltip would go off screen
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            # Update the tooltip to get its actual size
            self._tip.update_idletasks()
            tooltip_width = self._tip.winfo_reqwidth()
            tooltip_height = self._tip.winfo_reqheight()
            
            # Adjust x position if tooltip would go off right edge
            if x + tooltip_width > screen_width:
                x = screen_width - tooltip_width - 10
            
            # Adjust y position if tooltip would go off bottom edge
            if y + tooltip_height > screen_height:
                y = self.widget.winfo_rooty() - tooltip_height - 6
            
            self._tip.wm_geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Tooltip error: {e}")
            self._hide()

    def _hide(self):
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


