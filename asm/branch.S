.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       

li x1, 0
li x2, 4
beq x1, x2, blabel1
li x10, 1
beq x2, x0, blabel1
li x11, 1

blabel1:
ecall
