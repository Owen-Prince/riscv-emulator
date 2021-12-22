.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       

addi x1, x1, 4
addi x2, x1, 5

j jlabel 
ecall

jlabel:
li x3, 1
addi x1, x1, 4
ecall
