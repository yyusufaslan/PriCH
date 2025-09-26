import tkinter as tk

class Tooltip:
    def __init__(self, widget, text, delay_ms=300, pad_x=8, pad_y=4):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.pad_x = pad_x
        self.pad_y = pad_y
        self._after_id = None
        self._tip = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")

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

            label = tk.Label(
                self._tip,
                text=self.text,
                justify=tk.LEFT,
                background="#333333",
                foreground="#ffffff",
                relief=tk.SOLID,
                borderwidth=1,
                padx=self.pad_x,
                pady=self.pad_y,
                font=("Segoe UI", 9)
            )
            label.pack()

            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
            self._tip.wm_geometry(f"+{x}+{y}")
        except Exception:
            self._hide()

    def _hide(self):
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


