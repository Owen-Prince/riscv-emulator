#!/bin/bash

# do not add the asm subfolder name as a prefix
riscv64-unknown-elf-gcc -march=rv32i -mabi=ilp32 -nostdlib -nostartfiles -Tasm/link.ld -o asm/$1.o asm/$1.s