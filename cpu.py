#!/usr/bin/env python3
import struct
import glob
from elftools.elf.elffile import ELFFile

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

# class decode():
    # __init__(self, instr):

class Decode():
    ins = 0b0
    ins = 0b0
    opcode = 0b0
    rd = 0b0
    funct3 = 0b0
    rs1 = 0b0
    rs2 = 0b0
    funct7 = 0b0
    utype_imm20 = 0b0
    def __init__(self, ins):
        self.ins = ins
        self.opcode = self.gibi(6, 0)
        self.rd     = self.gibi(11, 7)
        self.funct3 = self.gibi(14, 12)
        self.rs1    = self.gibi(19, 15)
        self.rs2    = self.gibi(24, 20)
        self.funct7 = self.gibi(31, 25)
        self.utype_imm20  = self.gibi(31, 12)
    def __str__(self):
        return f"{Ops(self.opcode)}"[4:]

    def gibi(self, s, e):
        return (self.ins >> e) & ((1 << (s - e + 1))-1)





from enum import Enum
# RV32I Base Instruction Set
class Ops(Enum):
    LUI = 0b0110111        # load upper immediate
    LOAD = 0b0000011
    STORE = 0b0100011

    AUIPC = 0b0010111    # add upper immediate to pc
    BRANCH = 0b1100011
    JAL = 0b1101111
    JALR = 0b1100111

    IMM = 0b0010011
    OP = 0b0110011

    MISC = 0b0001111
    SYSTEM = 0b1110011

class Funct3(Enum):
    LB  = 0b000
    LH  = 0b001
    LW  = 0b010
    LBU = 0b100
    LHU = 0b101

    ADD = SUB = ADDI = 0b000
    SLLI = 0b001
    SLT = SLTI = 0b010
    SLTU = SLTIU = 0b011


    XOR = XORI = 0b100
    SRL = SRLI = SRA = SRAI = 0b101
    OR = ORI = 0b110
    AND = ANDI = 0b111

# 64k at 0x80000000
memory = b'\x00'*0x10000

def ws(dat, addr):
    global memory
    #print(hex(addr), len(dat))
    addr -= 0x80000000
    assert addr >=0 and addr < len(memory)
    memory = memory[:addr] + dat + memory[addr+len(dat):]

def r32(addr):
    addr -= 0x80000000
    assert addr >=0 and addr < len(memory)
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
    # Instruction Fetch
    ins = r32(regfile[PC])
    def gibi(s, e):
        return (ins >> e) & ((1 << (s - e + 1))-1)
    # Instruction Decodes
    opcode = gibi(6,0)
    f3 = gibi(14, 12)
    # print(opcode, f3)
    ins_d = Decode(ins)
    print("PC: %x --- %s" % (regfile[PC], ins_d))
    if (ins_d.opcode == Ops.LOAD):
        if (ins_d.funct3 == Funct3.LW):
            insaddr = regfile[ins_d.rs1] + gibi(31, 20)
            regfile[ins_d.rd] = r32[insaddr]

    elif (Ops(ins_d.opcode) == Ops.JAL):
        regfile[1] = regfile[PC] + 4
        regfile[PC] = (ins_d.utype_imm20 << 12)
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
