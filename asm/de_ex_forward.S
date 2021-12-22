.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       

li x1, 1
bne x1, x0, target 
ecall
target:
li x10, 1
ecall
