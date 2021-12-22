.section .text.init;                                            
.balign  4;                                                      
.globl _start;                                                  
_start:                                                                 
.balign 4;                                                       

li  x1, 0xD
lui x2, 0x80000
sw  x1, (x2)
ecall
