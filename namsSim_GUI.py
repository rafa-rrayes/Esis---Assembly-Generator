import tkinter as tk
from tkinter import filedialog
import re
class AssemblySimulator:
    def __init__(self):
        self.registers = {'%A': 0, '%D': 0}
        self.memoria = [0] * 16000
        self.program_counter = 0
        self.non_empty = []
        self.sections = {}
        self.funcoes = {
            'leaw': self.leaw,
            'movw': self.movw,
            'addw': self.addw,
            'subw': self.subw,
            'rsubw': self.rsubw,
            'incw': self.incw,
            'decw': self.decw,
            'notw': self.notw,
            'negw': self.negw,
            'andw': self.andw,
            'orw': self.orw,
            'jmp': self.jmp,
            'je': self.je,
            'jne': self.jne,
            'jg': self.jg,
            'jge': self.jge,
            'jl': self.jl,
            'jle': self.jle,
            'nop': self.nop
        }
        self.clockCycles = 0
        self.reg = r'%[AD]'
        self.mem = r'\(%[A]\)'
        self.im = r'\$(1|0|-1)'
        self.const = r'\$[0-9]+'
        self.section = r'\$[0-9a-zA-Z]+'
        self.argumentos = {
            'leaw': [f"{self.const}|{self.section}", self.reg],
            'movw': [f"{self.im}|{self.reg}|{self.mem}", f"{self.reg}|{self.mem}", f"({self.reg}|{self.mem})?", f"({self.reg}|{self.mem})?"],
            'addw': [f"{self.reg}|{self.mem}", f"{self.reg}|{self.mem}|{self.im}", f"{self.reg}|{self.mem}", f"{self.reg}|{self.mem})?", f"{self.reg}|{self.mem})?"],
            'subw': [f"{self.reg}|{self.mem}", f"{self.reg}|{self.mem}|{self.im}", f"{self.reg}|{self.mem}", f"{self.reg}|{self.mem})?", f"{self.reg}|{self.mem})?"],
            'rsubw': [f"{self.im}|{self.reg}|{self.mem}", f"{self.reg}|{self.mem}", self.reg, f"({self.reg})?", f"({self.reg})?"],
            'incw': [self.reg],
            'decw': [self.reg],
            'notw': [self.reg],
            'negw': [self.reg],
            'andw': [f"{self.reg}|{self.mem}", f"{self.reg}|{self.mem}"],
            'orw': [f"{self.reg}|{self.mem}", f"{self.reg}|{self.mem}"],
            'jmp': [],
            'je': [self.reg],
            'jne': [self.reg],
            'jg': [self.reg],
            'jge': [self.reg],
            'jl': [self.reg],
            'jle': [self.reg],
            'nop': []
        }   
    def prepare(self, code):
        code = code.split('\n')
        code = [i.strip() for i in code]
        code = [re.sub(r';.*', '', i) for i in code]
        code = [i for i in code if i != '']
        pc = 0
        for line in code:
            if line.endswith(':'):
                self.sections[line[:-1]] = pc
                pc += 1
                continue
            pc += 1
        return code
    def parseValue(self, arg):
        if arg[1] == 'registrador':
            return self.registers[arg[0]]
        if arg[1] == 'memoria':
            return self.memoria[self.registers['%A']]
        if arg[1] == 'imediato' or arg[1] == 'const':
            return int(arg[0][1:])
        raise Exception(f"linha {self.program_counter+1}: erro ao decifrar valor")
    def tipo(self, arg):
        if re.fullmatch(self.reg, arg):
            return 'registrador'
        if re.fullmatch(self.mem, arg):
            return 'memoria'
        if re.fullmatch(self.im, arg):
            return 'imediato'
        if re.fullmatch(self.const, arg):
            return 'const'
        if re.fullmatch(self.section, arg):
            return 'section'
        raise Exception(f"linha {self.program_counter+1}: tipo do argumento '{arg}' não pode ser identificado")
    def validar(self, op, args):
        if op not in self.funcoes:
            return "op não existe", op
        for i, argumento in enumerate(self.argumentos[op]):
            try:
                if not re.fullmatch(argumento, args[i]):
                    return "arg errado", args[i]
            except IndexError:
                if argumento[-1] != '?':
                    return "faltou arg" , argumento
        return False        

    def run(self):
        instructions = self.code
        while self.program_counter < len(instructions):
            instruction = instructions[self.program_counter].strip()
            self.execute_instruction(instruction)
            self.program_counter += 1
    def step(self):
        instruction = self.code[self.program_counter]
        self.execute_instruction(instruction)
        self.program_counter += 1
    def execute_instruction(self, instruction):
        if instruction.endswith(':'):
            return
        parts = instruction.split(' ')
        op = parts[0]
        args = ''.join(parts[1:]).split(',')
        valido = self.validar(op, args)
        if valido:
            if valido[0] == 'arg errado':
                print(self.code[self.program_counter])
                raise Exception(f"linha {self.program_counter+1}: Argumento {valido[1]} é invalido")
            if valido[0] == 'faltou arg':
                raise Exception(f"linha {self.program_counter+1}: Operação {op} está faltando argumento {valido[1]}")
            if valido[0] == "op não existe":
                raise Exception(f"linha {self.program_counter+1}: {op} não existe")
        else: # caso seja valido
            if op == 'jmp' or op == 'nop':
                self.funcoes[op]()
            else:
                tipos = [self.tipo(i) for i in args]
                args = list(zip(args, tipos))
                self.funcoes[op](args)
        self.clockCycles += 1
    def create_section(self, name):
        self.sections[name] = self.program_counter
    def leaw(self, args):
        if args[1][0] != '%A':
            raise Exception(f"linha {self.program_counter+1}: A operação de leaw só aceita o registrador %A")
        if args[0][1] == 'section':
            self.registers['%A'] = args[0][0][1:]
            return
        self.registers['%A'] = int(args[0][0][1:])

    def movw(self, args):
        valor = self.parseValue(args[0])
        for arg in args[1:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = valor
            elif arg[1] == 'memoria':
                self.memoria[self.registers['%A']] = valor
    def addw(self, args):
        value1 = self.parseValue(args[0])
        value2 = self.parseValue(args[1])
        result = value1 + value2
        for arg in args[2:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = result
            elif arg[1] == 'memoria':
                self.memoria[self.registers['%A']] = result
    def subw(self, args):
        value1 = self.parseValue(args[0])
        value2 = self.parseValue(args[1])
        result = value1 - value2
        for arg in args[2:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = result
            elif arg[1] == 'memoria':
                self.memoria[self.registers['%A']] = result
    def rsubw(self, args):
        value1 = self.parseValue(args[0])
        value2 = self.parseValue(args[1])
        result = value2 - value1
        for arg in args[2:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = result
            elif arg[1] == 'memoria':
                self.memoria[self.registers['%A']] = result
    def incw(self, args):
        self.registers[args[0][0]] = self.registers[args[0][0]]+1
    def decw(self, args):
        self.registers[args[0][0]] = self.registers[args[0][0]]-1
    def notw(self, args):
        self.registers[args[0][0]] = ~self.registers[args[0][0]]
    def negw(self, args):
        self.registers[args[0][0]] = -self.registers[args[0][0]]
    def andw(self, args):
        value1 = self.parseValue(args[0])
        value2 = self.parseValue(args[1])
        result = value1 & value2
        if args[2][1] == 'registrador':
            self.registers[args[2][0]] = result
        elif args[2][1] == 'memoria':
            self.memoria[self.registers['%A']] = result
    def orw(self, args):
        value1 = self.parseValue(args[0])
        value2 = self.parseValue(args[1])
        result = value1 | value2
        if args[2][1] == 'registrador':
            self.registers[args[2][0]] = result
        elif args[2][1] == 'memoria':
            self.memoria[self.registers['%A']] = result
    def jmp(self):
        self.program_counter = self.sections[self.registers['%A']]
    def je(self, args):
        if self.registers[args[0][0]] == 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jne(self, args):
        if self.registers[args[0][0]] != 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jg(self, args):
        if self.registers[args[0][0]] > 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jge(self, args):
        if self.registers[args[0][0]] >= 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jl(self, args):
        if self.registers[args[0][0]] < 0:
            self.program_counter = self.sections[self.registers['%A']]

    def jle(self, args):
        if self.registers[args[0][0]] <= 0:
            self.program_counter = self.sections[self.registers['%A']]
    def nop(self):
        pass
    def restart(self):
        self.registers = {'%A': 0, '%D': 0}
        self.memoria = [0] * 16000
        self.program_counter = 0
        self.sections = {}
        self.clockCycles = 0

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
        self.update_ram()
        self.code_editor.tag_remove("highlight", "1.0", "end")
        # Add highlight tag to the determined line
        self.code_editor.tag_add("highlight", f"{1}.0", f"{1}.end")
        self.clockCycles.config(text=f"Clock Cycles: 0")
        self.update_ram()
    def run(self):
        self.updateCode()
        self.SIM.run()
        self.update_ram()
        self.clockCycles.config(text=f"Clock Cycles: {self.SIM.clockCycles}")
    def step(self):
        self.SIM.step()
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
        self.SIM.assembly = self.code_editor.get(1.0, tk.END)
        self.SIM.code = self.SIM.prepare(self.SIM.assembly)
        
    def highlight_line(self):
        # Get all lines of text from the text editor
        lines = self.code_editor.get(1.0, tk.END).split('\n')
        # Stripping whitespace to identify truly empty lines
        lines = [line.strip() for line in lines]

        # This will be the real line in the editor to be highlighted
        line_number = 0  # Start from the first line, considering tkinter's indexing
        realCount = 0  # This will count non-empty/non-comment lines

        for line in lines:
            line_number += 1
            if line and line[0] != ';':  # Consider the line if it's not empty and not a comment
                realCount += 1
            if realCount == self.SIM.program_counter+2:
                break

        # Remove any previous highlights
        self.code_editor.tag_remove("highlight", "1.0", "end")
        # Add highlight tag to the determined line
        self.code_editor.tag_add("highlight", f"{line_number}.0", f"{line_number}.end")
        self.code_editor.see(f"{line_number}.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblySimulatorGUI(root)
    root.mainloop()