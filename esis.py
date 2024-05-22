import re
class Assembler:
    def __init__(self) -> None:
        pass
    def idLine(self, linha):
        if linha.startswith('while') and linha.endswith('{'):
            function = self.whileStart
        elif linha.startswith('if') and ':' in linha:
            function = self.ifStatement
        elif linha.startswith('def') and '{' in linha:
            function = self.DefFunc
        elif linha.endswith('()'):
            function = self.callFunc
        elif '=' in linha:
            function = self.setVariavel
        elif linha == '}':
            function = self.EndFunc
        else:
            print(linha)
            raise Exception(f"Syntax error in line {linha}")
        return function
    def condicao(self, condicao):
        """
        Recebe uma condição e retorna o assembly para a comparação e o jmp
        A comparação feita para os valores é feita apartir de uma subtração
        onde o 1 valor é subtraido do segundo e o resultado é salvo em %D
        EX:
        X < 4
        Salvamos X em D
        Salvamos 4 em A
        Subtraimos D de A e salvamos em D
        ou seja D = X - 4

        Como a comparação é um '<' menor, executamos o jmp se o valor de D for menor que 0
        """
        linha = condicao
        assembly = ''
        if '==' in linha:
            op = '=='
        elif '>=' in linha:
            op = '>='
        elif '>' in linha:
            op = '>'
        elif '<=' in linha:
            op = '<='
        elif '<' in linha:
            op = '<'
        elif '!=' in linha:
            op = '!='
        
        primeiroValor = linha.split(op)[0]
        segundoValor = linha.split(op)[1]

        if primeiroValor.isdecimal():
            assembly += f"""leaw ${primeiroValor}, %A
movw %A, %D\n"""
        else:
            if primeiroValor in self.variaveis:
                end = self.getVariavel(primeiroValor)
                assembly += f"""leaw ${end}, %A
movw (%A), %D\n"""
            else:
                raise Exception(f"{primeiroValor} not found in memory")
        if segundoValor.isdecimal():
            assembly += f"""leaw ${segundoValor}, %A\n"""
        else:
            if segundoValor in self.variaveis:
                end = self.getVariavel(segundoValor)
                assembly += f"""leaw ${end}, %A
movw (%A), %A\n"""
            else:
                raise Exception(f"{segundoValor} not found in memory")
        assembly += "subw %D, %A, %D"

        if op == '==':
            jmp = "je %D\nnop\n"
        if op == '!=':
            jmp = "jne %D\nnop\n"
        if op == '>':
            jmp = "jg %D\nnop\n"
        if op == '>=':
            jmp = "jge %D\nnop\n"
        if op == '<':
            jmp = "jl %D\nnop\n"
        if op == '<=':
            jmp = "jle %D\nnop\n"
        return assembly, jmp
    def addCode(self, code):
        self.code = code
    def getVariavel(self, nome):
        if nome not in self.variaveis.keys():
            if re.fullmatch(r'^R[1-9][0-9]*$', nome):
                endereco = int(nome[1:])
                if endereco in self.variaveis.values():
                    raise Exception(f"Endereço {endereco} já está sendo utilizado")
            elif len(list(self.variaveis.values())) >= 1:
                endereco = list(self.variaveis.values())[-1] + 1
                while endereco in self.variaveis.values():
                    endereco+=1
            else:
                endereco = 1
            self.variaveis[nome] = endereco
        else:
            endereco = self.variaveis[nome]
        return endereco
    def setVariavel(self, linha):

        assembly = ''
        content = linha.replace(' ', '').split('=')
        nome = content[0]
        valor = content[1]
        endereco = self.getVariavel(nome)
        # if + or - or | or & in linha
        if '+' in linha or '-' in linha or '|' in linha or '&' in linha:
            return self.Aritmetica(linha)
        elif '!' in linha or '-' in linha:
            return self.notNeg(linha)
        if valor.isdecimal():
            assembly = f"""leaw ${valor}, %A
movw %A, %D
leaw ${endereco}, %A
movw %D, (%A)\n"""
            return assembly
        else:
            if valor in self.variaveis:
                serCopiado = self.variaveis[valor]
                assembly += f"""leaw ${serCopiado}, %A
movw (%A), %D
leaw ${endereco}, %A
movw %D, (%A)\n"""
            else:
                raise Exception(f"{valor} not found in memory")
            return assembly
    def Aritmetica(self, linha):
        content = linha.replace(' ', '').split('=')
        nome = content[0]
        salvarEm = self.getVariavel(nome)
        assembly = ''
        if '+' in linha:
            sep = '+'
            comand = 'addw'
        elif '-' in linha:
            sep = '-'
            comand = 'subw'
        if '|' in linha:
            sep = '|'
            comand = 'orw'
        elif '&' in linha:
            sep = '&'
            comand = 'andw'
        primeiroValor = content[1].split(sep)[0]
        segundoValor = content[1].split(sep)[1]
        
        if segundoValor.isdecimal():
            assembly += f"""leaw ${segundoValor}, %A
movw %A, %D\n"""
        else:
            if segundoValor not in self.variaveis:
                raise Exception(f"{segundoValor} not found in memory")
            endereco = self.variaveis[segundoValor]
            assembly += f"""leaw ${endereco}, %A
movw (%A), %D\n"""
        if primeiroValor.isdecimal():
            assembly += f"leaw ${primeiroValor}, %A\n"
        else:
            if primeiroValor not in self.variaveis:
                raise Exception(f"{primeiroValor} not found in memory")
            endereco = self.variaveis[primeiroValor]
            assembly += f"""leaw ${endereco}, %A
movw (%A), %A\n"""
        assembly += f"""{comand} %A, %D, %D
leaw ${salvarEm}, %A
movw %D, (%A)\n"""
        return assembly
    def notNeg(self, linha):
        content = linha.replace(' ', '').split('=')
        letra = content[0]
        salvarEm = self.getVariavel(letra)
        operacao = content[1]
        operar = operacao[1:]
        assembly = ''
        if '!' in operacao:
            op = 'notw'
        elif '-' in operacao:
            op = 'negw'
        if operar.isdecimal():
            assembly += f"""leaw ${operar}, %A
movw %A, %D\n"""
        else:
            if operar in self.variaveis:
                end = self.getVariavel(operar)
                assembly += f"""leaw ${end}, %A
movw (%A), %D\n"""
            else:
                raise Exception(f"{operar} not found in memory")
        assembly += f"""{op} %D
leaw ${salvarEm}, %A
movw %D, (%A)\n"""
        return assembly        
    
    def whileStart(self, linha):
        self.whileNumber += 1
        self.functions.append(linha.strip()[6:][:-1].replace(' ', ''))
        inicio = f"""leaw $ENDWHILE{self.whileNumber}, %A
jmp
WHILE{self.whileNumber}:""" 
        return inicio
    def ifStatement(self, linha):
        assembly = ''
        linha = linha.replace(' ', '')
        ind = linha.index(':')
        func = linha[ind+1:]
        linha = linha[:ind]
        condicao = linha.replace('if', '')
        if '==' in condicao:
            condicao = condicao.replace('==', '!=')
        elif '!=' in condicao:
            condicao = condicao.replace('!=', '==')
        elif '>=' in condicao:
            condicao = condicao.replace('>=', '<')
        elif '<=' in condicao:
            condicao = condicao.replace('<=', '>')
        elif '>' in condicao:
            condicao = condicao.replace('>', '<=')
        elif '<' in condicao:
            condicao = condicao.replace('<', '>=')
        prepare, jmp = self.condicao(condicao)

        assembly += prepare+'\n'
        assembly+= f"leaw $ENDIF{func}, %A\n"
        assembly += jmp +'\n'
        assembly += f"""leaw $1024, %A
movw (%A), %D
incw %D
movw %D, (%A)
leaw $ENDIF{func}, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw ${func}, %A
jmp
nop
ENDIF{func}:"""
        return assembly    
    def DefFunc(self, linha):
        nome = linha[3:][:-1].strip()
        self.functions.append(nome+'()')
        inicio = f"""leaw $END{nome}, %A
jmp
nop
{nome}:"""
        return inicio
    def EndFunc(self, linha):
        if '()' in self.functions[-1]:
            nome = self.functions[-1][:-2]
            self.functions.pop()
            fim = f"""leaw $1024, %A
movw (%A), %A
movw %A, %D
decw %D
leaw $1024, %A
movw %D, (%A)
incw %D
movw %D, %A
movw (%A), %A
jmp
nop
END{nome}:"""
        else:
            condicao = self.functions[-1]
            self.functions.pop()
            fim = f'ENDWHILE{self.whileNumber}:\n'
            prepare, jmp = self.condicao(condicao)
            fim += prepare + '\n'
            fim += f"leaw $WHILE{self.whileNumber}, %A\n"
            fim += jmp
        return fim
    def callFunc(self, linha):
        nome = linha[:-2]
        assembly = f"""leaw $1024, %A
movw (%A), %A
movw %A, %D
incw %D
leaw $1024, %A
movw %D, (%A)
leaw $ENDCall{nome}, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw ${nome}, %A
jmp
nop
ENDCall{nome}:"""
        return assembly
    def parse(self, includeComent = False):
        self.variaveis = {}
        self.lastCallback = [1023]
        self.whileNumber = 0
        self.functions = []
        self.lineNumber = 1
        codigo = self.code.split('\n')
        assembly = 'leaw $1024, %A\nmovw %A, (%A)\n'
        for linha in codigo:
            comentario = ''
            if '#' in linha:
                comentario = ''.join(linha.split("#")[1:])
                linha = linha.split('#')[0]
            linha = linha.strip()
            if comentario != '' and includeComent:
                assembly += ';' + comentario + '\n'
            if linha != '':
                function = self.idLine(linha)
                assembly += function(linha).strip() + '\n'
        assembly.replace('\t', '')
        return assembly


if __name__ == '__main__':
    assmbl = Assembler()
    import sys
    path = sys.argv[1]
    includeComment = False
    if sys.argv[2] and sys.argv[2].lower() == 'includecomment':
        includeComment = True
    name = path.split('/')[-1].split('.')[0]
    with open(path, 'r') as file:
        codigo = file.read()
    assmbl.addCode(codigo)
    texto = assmbl.parse(includeComment)
    with open(path.replace('.esis', '.nasm'), 'w') as file:
        file.write(texto)
    print('Arquivo gerado com sucesso')