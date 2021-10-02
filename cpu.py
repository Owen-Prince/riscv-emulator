#!/usr/bin/env python3
import struct
import glob
from elftools.elf.elffile import ELFFile
from cpu_types import Ops, Funct3, opname
from decode import Decode

regfile = [0]*33
class Regfile:
    def __init__(self):
        self.regs = [0]*33
    def __getitem__(self, key):
        return self.regs[key]
    def __setitem__(self, key, value):
        if key == 0:
            return
        self.regs[key] = value & 0xFFFFFFFF

regfile = Regfile()
PC = 32

def ALU(aluop, a, b):
    if(aluop == Funct3.ADD):
        return a + b


# 64k at 0x80000000
memory = b'\x00'*0x10000
# memory = b'\x00'*0x4000


def ws(dat, addr):
    global memory
    addr -= 0x80000000
    if addr < 0 or addr >= len(memory):
        raise Exception("mem fetch to %x failed" % addr)

    # assert addr >=0 and addr < len(memory)
    memory = memory[:addr] + dat + memory[addr+len(dat):]

def r32(addr):
    addr -= 0x80000000
    # print(hex(addr), len(dat))
    if addr < 0 or addr >= len(memory):
        raise Exception("mem fetch to %x failed" % addr)
    # assert addr >=0 and addr < len(memory)
    return struct.unpack("<I", memory[addr:addr+4])[0]

def dump():
    pp = []
    for i in range(32):
        if i != 0 and i % 8 == 0:
            pp += "\n"
        pp += " %3s: %08x" % ("x%d" % i, regfile[i])
    pp += "\n    PC: %08x" % regfile[PC]
    print(''.join(pp))




def step():
    '''
    Advance clock cycle
    '''
    # Instruction Fetch
    ins = r32(regfile[PC])
    def gibi(s, e):
        return (ins >> e) & ((1 << (s - e + 1))-1)


    # Instruction Decodes
    ins_d = Decode(ins)

    print("PC: %x --- %s" % (regfile[PC], ins_d))

    if (ins_d.opcode == Ops.LOAD):
        if (ins_d.funct3 == Funct3.LW):
            insaddr = regfile[ins_d.rs1] + gibi(31, 20)
            regfile[ins_d.rd] = r32[insaddr]

    elif (Ops(ins_d.opcode) == Ops.JAL):
        regfile[1] = regfile[PC] + 4
        regfile[PC] = (ins_d.imm_j) + regfile[PC]

    elif(Ops(ins_d.opcode) == Ops.IMM):
        print(ins_d.funct3, regfile[ins_d.rs1], ins_d.imm_i)
        regfile[ins_d.rd] = ALU(ins_d.funct3, regfile[ins_d.rs1], ins_d.imm_i)

    # elif(ins_d.opcode == Ops.JAL):
    else:
        raise Exception("write op %x" % ins)

    regfile[PC] += 4



    return True
    dump()


if __name__ == "__main__":
    for x in glob.glob("riscv-tests/isa/rv32ui-p-*"):
        if x.endswith('.dump'):
            continue
        with open(x, 'rb') as f:
            print("test", x)
            e = ELFFile(f)
            for s in e.iter_segments():
                ws(s.data(), s.header.p_paddr)
            regfile[PC] = 0x80000000
            while step():
                pass
        break
