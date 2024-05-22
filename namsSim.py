import re
class AssemblySimulator:
    def __init__(self):
        self.registers = {'%A': 0, '%D': 0}
        self.memoria = [0] * 16000
        self.program_counter = 0
        self.codeLines = {}
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
    def loadCode(self, code):
        code = code.split('\n')
        code = [i.strip() for i in code]
        self.codeLines = {i: code[i] for i in range(len(code))}
        pc = 0
        for line in self.codeLines.values():
            if line.endswith(':'):
                self.sections[line[:-1]] = pc
                pc += 1
                continue
            pc += 1        
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
        instructions = self.codeLines
        while self.program_counter < (len(instructions)-1):
            self.step()
    def step(self):
        instruction = self.codeLines[self.program_counter]
        instruction = re.sub(r';.*', '', instruction)
        self.execute_instruction(instruction)
        self.program_counter += 1
        if not self.program_counter >= len(self.codeLines):
            instruction = self.codeLines[self.program_counter]
            instruction = re.sub(r';.*', '', instruction)
            while instruction.strip() == '' and self.program_counter < (len(self.codeLines)-1):
                self.program_counter += 1
                instruction = self.codeLines[self.program_counter]
                instruction = re.sub(r';.*', '', instruction)
        
    def execute_instruction(self, instruction):
        if instruction.endswith(':'):
            return
        parts = instruction.split(' ')
        op = parts[0]
        args = ''.join(parts[1:]).split(',')
        valido = self.validar(op, args)
        if valido:
            if valido[0] == 'arg errado':
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

# Example usage:
sim = AssemblySimulator()
instr = """leaw $1024, %A
movw %A, (%A)

;A=5

leaw $5, %A
movw %A, %D
leaw $1, %A
movw %D, (%A)



;C=A-1

leaw $1, %A
movw %A, %D
leaw $1, %A
movw (%A), %A
subw %A, %D, %D
leaw $2, %A
movw %D, (%A)

leaw $ENDfact, %A
jmp
nop
fact:


;B=C

leaw $2, %A
movw (%A), %D
leaw $3, %A
movw %D, (%A)



;Copia=A

leaw $1, %A
movw (%A), %D
leaw $4, %A
movw %D, (%A)



;multi()

leaw $ENDCallmulti, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
incw %A
movw %D, (%A)
leaw $1024, %A
movw (%A), %D
incw %D
movw %D, (%A)
leaw $multi, %A
jmp
nop
ENDCallmulti:


;C=C-1

leaw $1, %A
movw %A, %D
leaw $2, %A
movw (%A), %A
subw %A, %D, %D
leaw $2, %A
movw %D, (%A)



;ifC!=1:fact

leaw $2, %A
movw (%A), %D
leaw $1, %A
subw %D, %A, %D
leaw $ENDIFfact, %A
je %D
nop
leaw $1024, %A
movw (%A), %D
incw %D
movw %D, (%A)
leaw $ENDIFfact, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw $fact, %A
jmp
nop
ENDIFfact:
leaw $1024, %A
movw (%A), %D
decw %D
movw %D, (%A)
incw %D
movw %D, %A
movw (%A), %A
jmp
nop
ENDfact:
leaw $ENDmulti, %A
jmp
nop
multi:


;A=A+Copia

leaw $4, %A
movw (%A), %D
leaw $1, %A
movw (%A), %A
addw %A, %D, %D
leaw $1, %A
movw %D, (%A)



;B=B-1

leaw $1, %A
movw %A, %D
leaw $3, %A
movw (%A), %A
subw %A, %D, %D
leaw $3, %A
movw %D, (%A)



;ifB!=1:multi

leaw $3, %A
movw (%A), %D
leaw $1, %A
subw %D, %A, %D
leaw $ENDIFmulti, %A
je %D
nop
leaw $1024, %A
movw (%A), %D
incw %D
movw %D, (%A)
leaw $ENDIFmulti, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw $multi, %A
jmp
nop
ENDIFmulti:
leaw $1024, %A
movw (%A), %D
decw %D
movw %D, (%A)
incw %D
movw %D, %A
movw (%A), %A
jmp
nop
ENDmulti:


;fact()

leaw $ENDCallfact, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
incw %A
movw %D, (%A)
leaw $1024, %A
movw (%A), %D
incw %D
movw %D, (%A)
leaw $fact, %A
jmp
nop
ENDCallfact:"""
if __name__ == '__main__':
    sim.loadCode(instr)
    sim.run()
    print(sim.registers)
    print(sim.memoria[0:7])