#!/usr/bin/env python3
import struct
import glob
from elftools.elf.elffile import ELFFile
from cpu_types import Ops, Funct3
from decode_stage import Decode
from decode_stage import Utils

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







# 64k at 0x80000000
memory = b'\x00'*0x10000
# memory = b'\x00'*0x4000

def wcsr(dat, addr):
    '''data, address'''
    global memory
    memory = memory[:addr] + dat + memory[addr+len(dat):]

def r32csr(addr):
    return struct.unpack("<I", memory[addr:addr+4])[0]


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

# def pc_sel(btype):



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

    elif (ins_d.opcode == Ops.JAL):
        regfile[1] = regfile[PC] + 4
        regfile[PC] = (ins_d.imm_j) + regfile[PC]

    elif(ins_d.opcode == Ops.IMM):
        regfile[ins_d.rd] = ALU(ins_d.funct3, regfile[ins_d.rs1], ins_d.imm_i)

    elif(ins_d.opcode == Ops.BRANCH):
        if (ins_d.resolve_branch(regfile[ins_d.rs1], regfile[ins_d.rs2])):
            regfile[PC] += ins_d.imm_b

    elif(ins_d.opcode == Ops.AUIPC):
        regfile[PC] += ins_d.imm_u

    elif(ins_d.opcode == Ops.LUI):
        regfile[ins_d.rd] = ins_d.imm_u


    elif(ins_d.opcode == Ops.SYSTEM):
        # CSRRW reads the old value of the CSR, zero-extends the value to XLEN bits,
        # then writes it to integer register rd. The initial value in rs1 is written to the CSR
        regfile[ins_d.rd] = r32csr(ins_d.imm_i_unsigned)
        wcsr(struct.pack("I", regfile[ins_d.rs1]), ins_d.imm_i_unsigned)


        # LUI = 0b0110111        # load upper immediate

        # JALR = 0b1100111

        # BRANCH = 0b1100011

        # STORE = 0b0100011

        # OP = 0b0110011

        # MISC = 0b0001111

    # elif(ins_d.opcode == Ops.JAL):
    else:
        dump()
        raise Exception("write op %x" % ins)
    regfile[PC] += 4



    return True


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
