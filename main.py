import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from namsSim import AssemblySimulator
from tkinter import messagebox
import textwithLines as twl
from esis import Assembler
def bin_to_dec(x):
    try:
        num = str(x)
        result = int(f"{int(num[1:])*-1 if num[0] == '1' else int(num[1:])}", 2)
        return result
    except:
        return x
class AssemblySimulatorGUI:
    def __init__(self, master):
        self.SIM = AssemblySimulator()
        self.master = master
        master.title("Assembly Code Simulator")
        # Menu for file operations
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)
        self.assembler = Assembler()
        self.code_editor = twl.TextWithLineNumbers(master, height=20, width=60)
        self.code_editor.pack(expand=True, fill='both')
        self.code_editor.text.tag_configure("highlight", background="yellow")

        self.notebook = ttk.Notebook(root)
        
        self.tabEsis = ttk.Frame(self.notebook)
        self.tabSim = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tabEsis, text="Esis")
        self.notebook.add(self.tabSim, text="Simulador")
        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind("<<NotebookTabChanged>>", self.changeTab)
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.load_file)
        file_menu.add_command(label="Save As...", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=master.quit)

        # Assembly code editor
        
        self.infos = tk.Frame(self.tabSim)
        self.infos.pack(expand=True, fill='both', side=tk.TOP)
        # RAM list

        self.ram_view = tk.Listbox(self.infos, height=10, width=10)
        self.ram_view.pack(side=tk.LEFT, fill='both', expand=True)
        self.ram_viewBin = tk.Listbox(self.infos, height=10, width=25)
        self.ram_viewBin.pack(side=tk.LEFT, fill='both', expand=True)

        # Registers
        self.infosRight = tk.Frame(self.infos)
        self.infosRight.pack(side=tk.LEFT, fill='both', expand=True)
        self.infoRegs = tk.Label(self.infosRight, text="Registers")
        self.regsList = tk.Listbox(self.infoRegs, height=2, width=15)
        self.regsList.pack(side=tk.LEFT, fill='x', expand=True)
        self.regsListBin = tk.Listbox(self.infoRegs, height=2, width=20)
        self.regsListBin.pack(side=tk.LEFT, fill='x', expand=True)
        self.infoRegs.pack(side=tk.TOP, fill='x')

        self.clockCycles = tk.Label(self.infosRight, text="Clock Cycles: 0")
        self.clockCycles.pack(side=tk.TOP)
        
        self.update_ram()

        # Control buttons
        self.run_button = tk.Button(self.infosRight, text="Run", command=self.run)
        self.save_button = tk.Button(self.infosRight, text="Save", command=self.updateCode)
        self.step_button = tk.Button(self.infosRight, text="Step", command=self.step)
        self.restart_button = tk.Button(self.infosRight, text="Restart", command=self.restart)
        self.run_button.pack(side=tk.LEFT)
        self.save_button.pack(side=tk.LEFT)
        self.step_button.pack(side=tk.LEFT)
        self.restart_button.pack(side=tk.LEFT)


        self.buttonsEsis = tk.Frame(self.tabEsis)

        self.parseButton = tk.Button(self.buttonsEsis, text="Translate", command=self.translate)
        self.parseButton.pack(side=tk.LEFT)
    
        self.save_button = tk.Button(self.buttonsEsis, text="Save File", command=self.saveAssembly)
        self.save_button.pack(side=tk.LEFT)
        self.send_button = tk.Button(self.buttonsEsis, text="Translate and Send", command=self.sendAssembly)
        self.send_button.pack(side=tk.LEFT)
        self.buttonsEsis.pack(side=tk.TOP)

        # disable code viewer
        self.codeViwer = twl.TextWithLineNumbers(self.tabEsis, height=20, width=60)
        self.codeViwer.text.config(state='disabled')
        self.codeViwer.pack(expand=True, fill='both')
        self.ram_view.config(yscrollcommand=self.sync_scroll)
        self.ram_viewBin.config(yscrollcommand=self.sync_scroll)

        self.assembly = ''
        self.codeNasm = ''
        self.codeEsis = ''
        self.programSent = False

    def changeTab(self, event):
        if self.notebook.index(self.notebook.select()) == 0:
            self.codeNasm = self.code_editor.text.get(1.0, tk.END).strip()
            self.code_editor.text.delete(1.0, tk.END)
            self.code_editor.text.insert(tk.END, self.codeEsis)
            self.code_editor._on_update_line_numbers()
        elif self.notebook.index(self.notebook.select()) == 1:
            if self.programSent:
                self.programSent = False
                return
            self.codeEsis = self.code_editor.text.get(1.0, tk.END).strip()
            self.code_editor.text.delete(1.0, tk.END)
            self.code_editor.text.insert(tk.END, self.codeNasm)
            self.code_editor._on_update_line_numbers()
            self.highlight_line()
    def translate(self):
        
        self.assembler.addCode(self.code_editor.text.get(1.0, tk.END))
        self.assembly = self.assembler.parse(includeComent=True)
        self.codeViwer.text.config(state='normal')
        self.codeViwer.text.delete(1.0, tk.END)
        self.codeViwer.text.insert(tk.END, self.assembly)
        self.codeViwer.text.config(state='disabled')

    def saveAssembly(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("nasm file", "*.nasm")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.assembly)
    def sendAssembly(self):
        self.programSent = True
        self.codeEsis = self.code_editor.text.get(1.0, tk.END).strip()
        self.translate()
        self.notebook.select(1)
        
        self.code_editor.text.delete(1.0, tk.END)
        self.code_editor.text.insert(tk.END, self.assembly)
        self.restart()
        self.updateCode()
        self.update_ram()
        self.clockCycles.config(text=f"Clock Cycles: 0")
        self.code_editor._on_update_line_numbers()
    def restart(self):
        self.SIM.restart()
        self.SIM.loadCode(self.code_editor.text.get(1.0, tk.END))
        self.update_ram()

        self.highlight_line()
        self.clockCycles.config(text=f"Clock Cycles: 0")
    def run(self):
        self.updateCode()
        self.SIM.run()
        self.update_ram()
        self.clockCycles.config(text=f"Clock Cycles: {self.SIM.clockCycles}")
        self.code_editor.text.tag_remove("highlight", "1.0", "end")
    def step(self):
        self.SIM.step()
        self.update_ram()
        self.highlight_line()
        self.clockCycles.config(text=f"Clock Cycles: {self.SIM.clockCycles}")
    def sync_scroll(self,*args):
        self.ram_viewBin.yview('moveto', args[0])
        self.ram_view.yview('moveto', args[0])
    def update_ram(self):
        self.ram_view.delete(0, tk.END)  # Clear the Listbox
        self.ram_viewBin.delete(0, tk.END)
        for i, value in enumerate(self.SIM.memoria):
            decimal = bin_to_dec(value)
            binario = value
            self.ram_view.insert(tk.END, f'R{i}:  {decimal}')
            self.ram_viewBin.insert(tk.END, f'Binario:  {binario}')
        self.regsList.delete(0, tk.END)
        self.regsListBin.delete(0, tk.END)
        
        self.regsList.insert(tk.END, f'%A: {bin_to_dec(self.SIM.registers["%A"])}')
        self.regsListBin.insert(tk.END, f'Binario:  {self.SIM.registers["%A"]}')
        self.regsList.insert(tk.END, f'%D: {bin_to_dec(self.SIM.registers["%D"])}')
        self.regsListBin.insert(tk.END, f'Binario:  {self.SIM.registers["%D"]}')
    def load_file(self):
        if self.notebook.index(self.notebook.select()) == 0:
            file_path = filedialog.askopenfilename(filetypes=[("esis files", "*.esis"), ("All files", "*.*")])
        else:
            file_path = filedialog.askopenfilename(filetypes=[("nasm files", "*.nasm"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.code_editor.text.delete(1.0, tk.END)
                self.code_editor.text.insert(tk.END, file.read())
        self.code_editor._on_update_line_numbers()
        self.updateCode()
    def save_file(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("nasm file", "*.nasm")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.code_editor.text.get(1.0, tk.END))
        self.updateCode()    
    def updateCode(self):
        self.SIM.loadCode(self.code_editor.text.get(1.0, tk.END)) 
    def highlight_line(self):
        # Remove any previous highlights
        self.code_editor.text.tag_remove("highlight", "1.0", "end")
        # Add highlight tag to the determined line
        self.code_editor.text.tag_add("highlight", f"{self.SIM.program_counter+1}.0", f"{self.SIM.program_counter+1}.end")
        self.code_editor.text.see(f"{self.SIM.program_counter+1}.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblySimulatorGUI(root)
    root.geometry("800x600")
    root.mainloop()
