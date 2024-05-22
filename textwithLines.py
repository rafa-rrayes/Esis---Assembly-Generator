import tkinter as tk
from tkinter import ttk

class TextWithLineNumbers(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.ypos = 0
        self.line_numbers = tk.Text(self, width=4, padx=5, takefocus=0, border=0,
                                    background='grey', state='disabled', wrap='none')
        
        self.text = tk.Text(self, wrap='none')

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scroll)

        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.config(yscrollcommand=self._on_update_scrollbar)
        self.text.bind('<KeyRelease>', self._on_update_line_numbers)
        self.text.bind('<MouseWheel>', self._on_update_line_numbers)

        self._on_update_line_numbers()
        
    def _on_update_scrollbar(self, *args):
        self.scrollbar.set(*args)
        self._on_scroll(args[0], args[1])


    def _on_scroll(self, arg1, arg2):
        self.text.yview('moveto', arg1)
        self.ypos = float(arg1)
        self.line_numbers.yview('moveto', self.ypos)


    def _on_update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)

        line_count = int(self.text.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count+1))
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview('moveto', self.ypos)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Text Widget with Line Numbers")
    root.geometry("600x400")

    text_with_line_numbers = TextWithLineNumbers(root)
    text_with_line_numbers.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
