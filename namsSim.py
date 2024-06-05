import re
def dec_to_bin(num):
    try:
        dec = int(num)
        result = f'{0 if dec>=0 else 1}'+ f'{abs(dec):016b}'[1:]
        return result
    except:
        return num
def bin_to_dec(x):
    try:
        num = str(x)
        result = int(f"{int(num[1:])*-1 if num[0] == '1' else int(num[1:])}", 2)
        return result
    except:
        return x
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
            return self.memoria[bin_to_dec(self.registers['%A'])]
        if arg[1] == 'imediato' or arg[1] == 'const':
            return dec_to_bin(int(arg[0][1:]))
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
        self.registers['%A'] = dec_to_bin(int(args[0][0][1:]))

    def movw(self, args):
        valor = self.parseValue(args[0])
        for arg in args[1:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = valor
            elif arg[1] == 'memoria':
                self.memoria[bin_to_dec(self.registers['%A'])] = valor
    def addw(self, args):
        value1 = bin_to_dec(self.parseValue(args[0]))
        value2 = bin_to_dec(self.parseValue(args[1]))
        result = value1 + value2
        for arg in args[2:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = dec_to_bin(result)
            elif arg[1] == 'memoria':
                self.memoria[bin_to_dec(self.registers['%A'])] = dec_to_bin(result)
    def subw(self, args):
        value1 = bin_to_dec(self.parseValue(args[0]))
        value2 = bin_to_dec(self.parseValue(args[1]))
        result = value1 - value2
        for arg in args[2:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = dec_to_bin(result)
            elif arg[1] == 'memoria':
                self.memoria[bin_to_dec(self.registers['%A'])] = dec_to_bin(result)
    def rsubw(self, args):
        value1 = bin_to_dec(self.parseValue(args[0]))
        value2 = bin_to_dec(self.parseValue(args[1]))
        result = value2 - value1
        for arg in args[2:]:
            if arg[1] == 'registrador':
                self.registers[arg[0]] = dec_to_bin(result)
            elif arg[1] == 'memoria':
                self.memoria[bin_to_dec(self.registers['%A'])] = dec_to_bin(result)
    def incw(self, args):
        self.registers[args[0][0]] = dec_to_bin(bin_to_dec(self.registers[args[0][0]])+1)
    def decw(self, args):
        self.registers[args[0][0]] = dec_to_bin(bin_to_dec(self.registers[args[0][0]])-1)
    def notw(self, args):
        num = self.registers[args[0][0]]
        num = num.replace('0', '2')
        num = num.replace('1', '0')
        num = num.replace('2', '1')
        self.registers[args[0][0]] = num
    def negw(self, args):
        self.registers[args[0][0]] = dec_to_bin(-bin_to_dec(self.registers[args[0][0]]))
    def andw(self, args):
        value1 = self.parseValue(args[0])
        value2 = self.parseValue(args[1])
        result = ''
        for i, j in zip(value1, value2):
            if i == '1' and j == '1':
                result += '1'
            else:
                result += '0'
        if args[2][1] == 'registrador':
            self.registers[args[2][0]] = result
        elif args[2][1] == 'memoria':
            self.memoria[bin_to_dec(self.registers['%A'])] = result
    def orw(self, args):
        value1 = self.parseValue(args[0])
        value2 = self.parseValue(args[1])
        result = ''
        for i, j in zip(value1, value2):
            if i == '1' or j == '1':
                result += '1'
            else:
                result += '0'
        if args[2][1] == 'registrador':
            self.registers[args[2][0]] = result
        elif args[2][1] == 'memoria':
            self.memoria[bin_to_dec(self.registers['%A'])] = result
    def jmp(self):
        self.program_counter = self.sections[self.registers['%A']]
    def je(self, args):
        if bin_to_dec(self.registers[args[0][0]]) == 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jne(self, args):
        if bin_to_dec(self.registers[args[0][0]]) != 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jg(self, args):
        if bin_to_dec(self.registers[args[0][0]]) > 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jge(self, args):
        if bin_to_dec(self.registers[args[0][0]]) >= 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jl(self, args):
        if bin_to_dec(self.registers[args[0][0]]) < 0:
            self.program_counter = self.sections[self.registers['%A']]
    def jle(self, args):
        if bin_to_dec(self.registers[args[0][0]]) <= 0:
            self.program_counter = self.sections[self.registers['%A']]
    def nop(self):
        pass
    def restart(self):
        self.registers = {'%A': 0, '%D': 0}
        self.memoria = [0] * 16000
        self.program_counter = 0
        self.sections = {}
        self.clockCycles = 0


if __name__ == '__main__':
    sim = AssemblySimulator()
    instr = """leaw $1024, %A
movw %A, (%A)
leaw $5, %A
movw %A, %D
leaw $1, %A
movw %D, (%A)
leaw $1, %A
movw (%A), %D
leaw $2, %A
movw %D, (%A)
"""
    sim.loadCode(instr)
    sim.run()
    print(sim.registers)
    print(sim.memoria[0:7])
