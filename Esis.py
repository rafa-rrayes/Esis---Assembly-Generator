
variaveis = {}
lastCallback = [1023]
whileNumber = 0
def getVariavel(nome):
    if nome not in variaveis.keys():
        if len(list(variaveis.values())) >= 1:
            endereco = list(variaveis.values())[-1] + 1
            while endereco in variaveis.values():
                endereco+=1
        else:
            endereco = 1
        variaveis[nome] = endereco
    else:
        endereco = variaveis[nome]
    return endereco
def setVariavel(linha):
    assembly = ''
    content = linha.replace(' ', '').split('=')
    nome = content[0]
    valor = content[1]
    endereco = getVariavel(nome)
    if valor.isdecimal():
        assembly = f"""leaw ${valor}, %A
movw %A, %D
leaw ${endereco}, %A
movw %D, (%A)\n"""
        return assembly
    else:
        if valor in variaveis:
            serCopiado = variaveis[valor]
            assembly += f"""leaw ${serCopiado}, %A
movw (%A), %D
leaw ${endereco}, %A
movw %D, (%A)\n"""
        else:
            raise Exception(f"{valor} not found in memory")
        return assembly
def somaSub(linha):
    content = linha.replace(' ', '').split('=')
    nome = content[0]
    if '+' in linha:
        sep = '+'
        comand = 'addw'
    elif '-' in linha:
        sep = '-'
        comand = 'subw'
    primeiroValor = content[1].split(sep)[0]
    segundoValor = content[1].split(sep)[1]
    salvarEm = getVariavel(nome)
    assembly = ''
    if segundoValor.isdecimal():
        assembly += f"""leaw ${segundoValor}, %A
movw %A, %D\n"""
    else:
        if segundoValor not in variaveis:
            raise Exception(f"{segundoValor} not found in memory")
        endereco = variaveis[segundoValor]
        assembly += f"""leaw ${endereco}, %A
movw (%A), %D\n"""
    if primeiroValor.isdecimal():
        assembly += f"leaw ${primeiroValor}, %A\n"
    else:
        if primeiroValor not in variaveis:
            raise Exception(f"{primeiroValor} not found in memory")
        endereco = variaveis[primeiroValor]
        assembly += f"""leaw ${endereco}, %A
movw (%A), %A\n"""
    assembly += f"""{comand} %A, %D, %D
leaw ${salvarEm}, %A
movw %D, (%A)\n"""
    return assembly
def notNeg(linha):
    content = linha.replace(' ', '').split('=')
    letra = content[0]
    salvarEm = getVariavel(letra)
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
        if operar in variaveis:
            end = getVariavel(operar)
            assembly += f"""leaw ${end}, %A
movw (%A), %D\n"""
        else:
            raise Exception(f"{operar} not found in memory")
    assembly += f"""{op} %D
leaw ${salvarEm}, %A
movw %D, (%A)\n"""
    return assembly
    
  
def orAnd(linha):
    content = linha.replace(' ', '').split('=')
    letra = content[0]
    salvarEm = getVariavel(letra)
    operacao = content[1]
    assembly = ''
    if '|' in operacao:
        op = 'orw'
        simbolo = '|'
    elif '&' in operacao:
        op = 'andw'
        simbolo = '&'
    primeiroValor = operacao.split(simbolo)[0]
    segundoValor = operacao.split(simbolo)[1]
    if primeiroValor.isdecimal():
        assembly += f"""leaw ${primeiroValor}, %A
movw %A, %D"""
    else:
        if primeiroValor in variaveis:
            end = getVariavel(primeiroValor)
            assembly += f"""leaw ${end}, %A
movw (%A), %D"""
        else:
            raise Exception(f"{primeiroValor} not found in memory")
    if segundoValor.isdecimal():
        assembly += f"""leaw ${segundoValor}, %A\n"""
    else:
        if segundoValor in variaveis:
            end = getVariavel(segundoValor)
            assembly += f"""leaw ${end}, %A
movw (%A), %A"""
        else:
            raise Exception(f"{segundoValor} not found in memory")
    assembly += f"""{op} %D, %A, %D
leaw ${salvarEm}, %A
movw %D, (%A)"""
    return assembly

def whileStart(whileNumber):
    inicio = f"""leaw $ENDWHILE{whileNumber}, %A
jmp
WHILE{whileNumber}:
""" 
    return inicio
def whileEnd(linha, whileNumber):
    condicao = linha[6:][:-1]
    if '==' in condicao:
        op = '=='
    elif '>=' in condicao:
        op = '>='
    elif '>' in condicao:
        op = '>'
    elif '<=' in condicao:
        op = '<='
    elif '<' in condicao:
        op = '<'
    elif '!=' in condicao:
        op = '!='
    condicao = condicao.replace(' ', '')
    primeiroValor, segundoValor = condicao.split(op)
    fim = f'ENDWHILE{whileNumber}:\n'
    if primeiroValor.isdecimal():
        fim += f"""leaw ${primeiroValor}, %A
movw %A, %D\n"""
    else:
        if primeiroValor in variaveis:
            end = getVariavel(primeiroValor)
            fim += f"""leaw ${end}, %A
movw (%A), %D\n"""
        else:

            raise Exception(f"{primeiroValor} not found in memory")
    if segundoValor.isdecimal():
        fim += f"""leaw ${segundoValor}, %A\n"""
    else:
        if segundoValor in variaveis:
            end = getVariavel(segundoValor)
            fim += f"""leaw ${end}, %A
movw (%A), %A\n"""
        else:
            raise Exception(f"{segundoValor} not found in memory")
    fim += f"""subw %D, %A, %D
leaw $WHILE{whileNumber}, %A"""
    if op == '==':
        fim += "je %D\nnop\n"
    if op == '!=':
        fim += "jne %D\nnop\n"
    if op == '>':
        fim += "jg %D\nnop\n"
    if op == '>=':
        fim += "jge %D\nnop\n"
    if op == '<':
        fim += "jl %D\nnop\n"
    if op == '<=':
        fim += "jle %D\nnop\n"
    return fim
def ifStatement(linha):
    assembly = ''
    linha = linha.replace(' ', '')
    ind = linha.index(':')
    func = linha[ind+1:]
    linha = linha[:ind]
    linha = linha.replace('if', '')
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
        if primeiroValor in variaveis:
            end = getVariavel(primeiroValor)
            assembly += f"""leaw ${end}, %A
movw (%A), %D\n"""
        else:
            raise Exception(f"{primeiroValor} not found in memory")
    if segundoValor.isdecimal():
        assembly += f"""leaw ${segundoValor}, %A\n"""
    else:
        if segundoValor in variaveis:
            end = getVariavel(segundoValor)
            assembly += f"""leaw ${end}, %A
movw (%A), %A\n"""
        else:
            raise Exception(f"{segundoValor} not found in memory")
    assembly += f"""subw %D, %A, %D
leaw $ENDIF{func}, %A\n"""
    if op == '==':
        assembly += "jne %D\nnop\n"
    if op == '!=':
        assembly += "je %D\nnop\n"
    if op == '>':
        assembly += "jle %D\nnop\n"
    if op == '>=':
        assembly += "jl %D\nnop\n"
    if op == '<':
        assembly += "jg %D\nnop\n"
    if op == '<=':
        assembly += "jge %D\nnop\n"
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

def callFunc(linha):
    nome = linha[:-2]


    assembly = f"""leaw $ENDCall{nome}, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
incw %A
movw %D, (%A)
leaw $1024, %A
movw (%A), %D
incw %D
movw %D, (%A)
leaw ${nome}, %A
jmp
nop
ENDCall{nome}:"""
    return assembly
def DefFunc(nome):
    inicio = f"""
leaw $END{nome}, %A
jmp
nop
{nome}:
"""
    
    return inicio
def EndFunc(nome):
    fim = f"""
leaw $END{nome}, %A
jmp
nop
{nome}:
"""
    
    return fim
def parse(codigo):
    funcoes = []
    whileNumber = 0
    codigo = codigo.split('\n')
    last = []
    assembly = 'leaw $1024, %A\nmovw %A, (%A)\n'
    for i in range (len(codigo)):
        linha = codigo[i].strip()
        if 'if' in linha and ':' in linha:
            function = ifStatement
        elif '=' in linha and ('+' in linha or '-' in linha):
            function = somaSub
        elif '=' in linha and ('&' in linha or '|' in linha):
            function = orAnd
        elif '=' in linha and ('-' in linha or '!' in linha):
            function = notNeg
        elif '=' in linha:
            function = setVariavel     
        elif '()' in linha:
            function = callFunc
        elif linha.startswith('def '):
            nome = linha[3:][:-1].strip()
            funcoes.append(nome)
            assembly+= DefFunc(nome) +'\n'
            last.append('funcao')
            continue
        elif linha.startswith('while '):
            assembly += whileStart(whileNumber)
            funcoes.append(linha)
            whileNumber += 1
            continue
        elif linha.strip() == '}':
            if last[-1] == 'funcao':
                assembly += EndFunc(funcoes[-1])
                funcoes.pop()
            elif last[-1] == 'while':
                assembly += whileEnd(funcoes[-1])
                funcoes.pop()
                whileNumber -= 1
            continue
        elif linha.strip() == '':
            continue
        # else:
        #     print(linha, 'ooo')
        # print(linha)
        assembly+= function(linha) +'\n'
    # assembly = assembly.replace('\t', '').replace(' ', '')
    return assembly


codigoFatorial = """
A = 5
C = A -1 
def fact{
    B = C
    Copia = A
    multi()
    C = C-1
    if C != 1: fact
}
def multi{
    while B > 1{
        A = A+Copia
        B = B-1
    }
}
fact()
"""
codigoQuadrado = """
A = 0
B = 5
while A < 10{
    A = A + 1
    B = B + 3
}
"""

print(parse(codigoFatorial))

