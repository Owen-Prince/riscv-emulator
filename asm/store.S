.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       

lui x1, 0x80000
li x2, 4
li x10, 1
nop
nop
nop
nop
sw x2, 0(x1)
li x11, 1

blabel1:
ecall
