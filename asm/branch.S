.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       
# screw boot code, we're going minimalist
# mtohost is the CSR in machine mode

nop
nop
beq x1, x2, blabel1
li x1, 4

blabel1:
bne x1, x2, blabel2
li x1, 4
blabel2:
addi x1, x2, 4
ecall
