import tkinter as tk
from tkinter import filedialog
from namsSim import AssemblySimulator
from tkinter import messagebox
class AssemblySimulatorGUI:
    def __init__(self, master):
        self.SIM = AssemblySimulator()
        self.master = master
        master.title("Assembly Code Simulator")
        # Menu for file operations
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.load_file)
        file_menu.add_command(label="Save As...", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=master.quit)

        # Assembly code editor
        self.code_editor = tk.Text(master, height=20, width=60)
        self.code_editor.pack()
        self.code_editor.tag_configure("highlight", background="yellow")

        # RAM list
        self.ram_view = tk.Listbox(master, height=10, width=45)
        self.ram_view.pack()

        # Registers
        self.cu = tk.Listbox(master, height=2, width=30)
        self.cu.pack()
        self.update_ram()
        # Control buttons
        self.run_button = tk.Button(master, text="Run", command=self.run)
        self.save_button = tk.Button(master, text="Save", command=self.updateCode)
        self.step_button = tk.Button(master, text="Step", command=self.step)
        self.restart_button = tk.Button(master, text="Restart", command=self.restart)

        self.run_button.pack(side=tk.LEFT)
        self.save_button.pack(side=tk.LEFT)
        self.step_button.pack(side=tk.LEFT)
        self.restart_button.pack(side=tk.LEFT)
        self.clockCycles = tk.Label(master, text="Clock Cycles: 0")
        self.clockCycles.pack()
    def restart(self):
        self.SIM.restart()
        self.SIM.loadCode(self.code_editor.get(1.0, tk.END))
        self.update_ram()

        self.code_editor.tag_remove("highlight", "1.0", "end")
        # Add highlight tag to the determined line
        self.code_editor.tag_add("highlight", f"{1}.0", f"{1}.end")
        self.clockCycles.config(text=f"Clock Cycles: 0")
    def run(self):
        self.updateCode()
        try:
            self.SIM.run()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self.update_ram()
        self.clockCycles.config(text=f"Clock Cycles: {self.SIM.clockCycles}")
    def step(self):
        try:
            self.SIM.step()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self.update_ram()
        self.highlight_line()
        self.clockCycles.config(text=f"Clock Cycles: {self.SIM.clockCycles}")

    def update_ram(self):
        self.ram_view.delete(0, tk.END)  # Clear the Listbox
        for i, value in enumerate(self.SIM.memoria):
            self.ram_view.insert(tk.END, f'R{i}: {value}                                           {0:016b}')
        self.cu.delete(0, tk.END)
        self.cu.insert(tk.END, f'%A: {self.SIM.registers["%A"]}               binary: {0:016b}')
        self.cu.insert(tk.END, f'%D: {self.SIM.registers["%D"]}               binary: {0:016b}')
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(tk.END, file.read())
        self.updateCode()
    def save_file(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.code_editor.get(1.0, tk.END))
        self.updateCode()    
    def updateCode(self):
        self.SIM.loadCode(self.code_editor.get(1.0, tk.END))        
    def highlight_line(self):
      
        # Remove any previous highlights
        self.code_editor.tag_remove("highlight", "1.0", "end")
        # Add highlight tag to the determined line
        self.code_editor.tag_add("highlight", f"{self.SIM.program_counter+1}.0", f"{self.SIM.program_counter+1}.end")
        self.code_editor.see(f"{self.SIM.program_counter+1}.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblySimulatorGUI(root)
    root.mainloop()