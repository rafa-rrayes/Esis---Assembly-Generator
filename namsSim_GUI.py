import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from namsSim import AssemblySimulator
from tkinter import messagebox
import textwithLines as twl
from esis import Assembler

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
        self.tabSim = ttk.Frame(self.notebook)
        self.tabEsis = ttk.Frame(self.notebook)
        self.notebook.add(self.tabSim, text="Simulador")
        self.notebook.add(self.tabEsis, text="Esis")
        self.notebook.pack(expand=True, fill='both')

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

        # disable code viewe
        self.codeViwer = twl.TextWithLineNumbers(self.tabEsis, height=20, width=60)
        self.codeViwer.text.config(state='disabled')
        self.codeViwer.pack(expand=True, fill='both')
        self.assembly = ''
        self.ram_view.config(yscrollcommand=self.sync_scroll)
        self.ram_viewBin.config(yscrollcommand=self.sync_scroll)
    def translate(self):
        
        self.assembler.addCode(self.code_editor.text.get(1.0, tk.END))
        
        self.codeViwer.text.config(state='normal')
        self.codeViwer.text.delete(1.0, tk.END)
        self.codeViwer.text.insert(tk.END, self.assembly)
        self.codeViwer.text.config(state='disabled')

    def saveAssembly(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("Text files", "*.nasm")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.assembly)
    def sendAssembly(self):
        self.assembler.addCode(self.code_editor.text.get(1.0, tk.END))
        self.assembly = self.assembler.parse()
        self.notebook.select(0)
        self.code_editor.text.delete(1.0, tk.END)
        self.code_editor.text.insert(tk.END, self.assembly)

        self.updateCode()
        self.update_ram()
        self.code_editor.text.tag_remove("highlight", "1.0", "end")
        # Add highlight tag to the determined line
        self.code_editor.text.tag_add("highlight", f"{1}.0", f"{1}.end")
        self.clockCycles.config(text=f"Clock Cycles: 0")
    def restart(self):
        self.SIM.restart()
        self.SIM.loadCode(self.code_editor.text.get(1.0, tk.END))
        self.update_ram()

        self.code_editor.text.tag_remove("highlight", "1.0", "end")
        # Add highlight tag to the determined line
        self.code_editor.text.tag_add("highlight", f"{1}.0", f"{1}.end")
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
    def sync_scroll(self,*args):
        self.ram_viewBin.yview('moveto', args[0])
        self.ram_view.yview('moveto', args[0])
        

    def update_ram(self):
        self.ram_view.delete(0, tk.END)  # Clear the Listbox
        self.ram_viewBin.delete(0, tk.END)
        for i, value in enumerate(self.SIM.memoria):
            self.ram_view.insert(tk.END, f'R{i}:  {value}')
            try:
                self.ram_viewBin.insert(tk.END, f'Binario:  {int(value):016b}')
            except:
                self.ram_viewBin.insert(tk.END, f'Binario:  {value}')
        self.regsList.delete(0, tk.END)
        self.regsList.insert(tk.END, f'%A: {self.SIM.registers["%A"]}')
        try:
            self.regsListBin.insert(tk.END, f'Binario:  {int(self.SIM.registers["%A"]):016b}')
        except:
            self.regsListBin.insert(tk.END, f'Binario:  {self.SIM.registers["%A"]}')
        self.regsList.insert(tk.END, f'%D: {self.SIM.registers["%D"]}')
        try:
            self.regsListBin.insert(tk.END, f'Binario:  {int(self.SIM.registers["%D"]):016b}')
        except:
            self.regsListBin.insert(tk.END, f'Binario:  {self.SIM.registers["%D"]}')
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("esis files", "*.esis"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.code_editor.text.delete(1.0, tk.END)
                self.code_editor.text.insert(tk.END, file.read())
        self.updateCode()
    def save_file(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("Text files", "*.txt")])
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
