.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       
        /* reset vector */                                              
j trap_vector;                                                 
trap_vector: 
# screw boot code, we're going minimalist
# mtohost is the CSR in machine mode
addi x1, x1, 4
addi x2, x1, 5

j jlabel 
ecall

jlabel:
li x3, 1
nop
nop
nop
nop
nop
nop
nop
nop
addi x1, x1, 4
ecall
