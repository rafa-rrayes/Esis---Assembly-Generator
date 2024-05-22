leaw $1024, %A
movw %A, (%A)
; Calcular fatorial de 6
leaw $6, %A
movw %A, %D
leaw $1, %A
movw %D, (%A)
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
leaw $ENDWHILE1, %A
jmp
WHILE1:
leaw $2, %A
movw (%A), %D
leaw $3, %A
movw %D, (%A)
leaw $1, %A
movw (%A), %D
leaw $4, %A
movw %D, (%A)
leaw $1024, %A
movw (%A), %A
movw %A, %D
incw %D
leaw $1024, %A
movw %D, (%A)
leaw $ENDCallmulti, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw $multi, %A
jmp
nop
ENDCallmulti:
leaw $1, %A
movw %A, %D
leaw $2, %A
movw (%A), %A
subw %A, %D, %D
leaw $2, %A
movw %D, (%A)
ENDWHILE1:
leaw $2, %A
movw (%A), %D
leaw $1, %A
subw %D, %A, %D
leaw $WHILE1, %A
jg %D
nop
leaw $1024, %A
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
ENDfact:
leaw $ENDmulti, %A
jmp
nop
multi:
leaw $ENDWHILE2, %A
jmp
WHILE2:
leaw $4, %A
movw (%A), %D
leaw $1, %A
movw (%A), %A
addw %A, %D, %D
leaw $1, %A
movw %D, (%A)
leaw $1, %A
movw %A, %D
leaw $3, %A
movw (%A), %A
subw %A, %D, %D
leaw $3, %A
movw %D, (%A)
ENDWHILE2:
leaw $3, %A
movw (%A), %D
leaw $1, %A
subw %D, %A, %D
leaw $WHILE2, %A
jg %D
nop
leaw $1024, %A
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
ENDmulti:
leaw $1024, %A
movw (%A), %A
movw %A, %D
incw %D
leaw $1024, %A
movw %D, (%A)
leaw $ENDCallfact, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw $fact, %A
jmp
nop
ENDCallfact:
; Salvar resultado no endereço 0
leaw $1, %A
movw (%A), %D
leaw $0, %A
movw %D, (%A)

