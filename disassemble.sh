#!/bin/bash

# do not add the asm subfolder name as a prefix
riscv64-unknown-elf-objdump -d asm/$1.o > asm/$1_actual