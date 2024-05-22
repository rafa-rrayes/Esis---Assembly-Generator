leaw $1024, %A
movw %A, (%A)
; dividendo = 216
leaw $216, %A
movw %A, %D
leaw $1, %A
movw %D, (%A)
; divisor = 6
leaw $6, %A
movw %A, %D
leaw $2, %A
movw %D, (%A)
leaw $0, %A
movw %A, %D
leaw $3, %A
movw %D, (%A)
leaw $ENDsub1, %A
jmp
nop
sub1:
leaw $1, %A
movw %A, %D
leaw $3, %A
movw (%A), %A
subw %A, %D, %D
leaw $3, %A
movw %D, (%A)
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
ENDsub1:
leaw $ENDdivisao, %A
jmp
nop
divisao:
leaw $ENDWHILE1, %A
jmp
WHILE1:
leaw $2, %A
movw (%A), %D
leaw $1, %A
movw (%A), %A
subw %A, %D, %D
leaw $1, %A
movw %D, (%A)
leaw $1, %A
movw %A, %D
leaw $3, %A
movw (%A), %A
addw %A, %D, %D
leaw $3, %A
movw %D, (%A)
leaw $1, %A
movw (%A), %D
leaw $0, %A
subw %D, %A, %D
leaw $ENDIFsub1, %A
jge %D
nop

leaw $1024, %A
movw (%A), %D
incw %D
movw %D, (%A)
leaw $ENDIFsub1, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw $sub1, %A
jmp
nop
ENDIFsub1:
ENDWHILE1:
leaw $1, %A
movw (%A), %D
leaw $0, %A
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
ENDdivisao:
leaw $1024, %A
movw (%A), %A
movw %A, %D
incw %D
leaw $1024, %A
movw %D, (%A)
leaw $ENDCalldivisao, %A
movw %A, %D
leaw $1024, %A
movw (%A), %A
movw %D, (%A)
leaw $divisao, %A
jmp
nop
ENDCalldivisao:
; salvar resultado em R0
leaw $3, %A
movw (%A), %D
leaw $0, %A
movw %D, (%A)

