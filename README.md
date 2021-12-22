# riscv-emulator

Based on [twitchcore](https://github.com/geohot/twitchcore) from George Hotz. The goal is to emulate the architecture of an in-order pipelined RISC-V processor.

### Modules:  
1. Pipeline stages:
   1. Fetch
   2. Decode 
   3. Execute
   4. Memory
   5. Writeback
2.  RAM (not hardware accurate DRAM, though)
3.  Forwarding unit
4.  Hazard unit

I started the development process off of an early commit of twitchcore and developed a working single-cycle version. This has evolved into the current processor.

## Current state
- Passes loads and stores in unit tests
- Exhibits proper forwarding behavior for instructions in decode, execute and mem stages
- Passes tests under `riscv-tests/isa/rv32ui-p-*` subfolders
- Load-use case has not been verified

## Future work
- Make RAM multicycle and more hardware-accurate
- Add caches
- Resolve branches in execute or memory stage and add branch prediction
- Support more extensions (Zicsr, M, D)

## Getting Started


Follow these steps to set up riscv-tests

    $ git clone https://github.com/riscv/riscv-tests
    $ cd riscv-tests
    $ git submodule update --init --recursive
    $ autoconf
    $ ./configure --prefix=$RISCV/target
    $ make
    $ make install


### Executing program

To run on the riscv-tests repository:

    $ python3 run_riscv_tests.py

To run on a custom assembly file (for example, asm/branch.S):

Assemble first using the `assemble.sh` bash script. It assumes the assembly file is in the asm/ subfolder; the argument should not contain the "asm/" prefix or the ".s" extension.

    $ ./assemble.sh branch
    $ python3 run.py branch.o

A trace will be generated in `trace.log` 

## License

This project is licensed under the MIT License - see the LICENSE file for details

