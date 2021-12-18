#!/bin/bash

riscv64-unknown-elf-objdump -d asm/$1.o > asm/$1_actual