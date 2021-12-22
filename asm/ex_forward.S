.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       

li x1, 1
addi x10, x1, 1
addi x11, x1, 2
addi x12, x1, 3
addi x13, x12, 3
addi x14, x13, 3
ecall
