#!/usr/bin/env python3
import binascii
import glob
import os
import struct
import logging

from elftools.elf.elffile import ELFFile

from cpu_types import Funct3, Ops, Utils
from decode_stage import Decode
from execute_stage import Execute
from fetch_stage import Fetch
from mem_stage import Mem
from wb_stage import Wb

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

class CSregs():
    def __init__(self):
        self.modified = {}
        self.cregs =  b'\x00'*0x4000
    def __getitem__(self, key):
        addr = key << 2
        return struct.unpack("<I", self.cregs[addr:addr+4])[0]
    def __setitem__(self, key, val):
        addr = key << 2
        dat = struct.pack("<I", val & 0xFFFFFFFF) 
        self.cregs = self.cregs[:addr] + dat + self.cregs[addr+len(dat):]
        self.modified[key] = dat
        logging.info("0x%s:  %s", key, Utils.zext(struct.unpack('<I', dat)[0]))
    def print_modified(self):
        for key, value in self.modified.items():
            print(f'0x{key:x}:  {Utils.zext(struct.unpack("<I", value)[0]):s}')
    def __str__(self):
        s = ""
        for key, value in self.modified.items():
            s = s + f'0x{key:x}:  {Utils.zext(struct.unpack("<I", value)[0]):s}\n'

        return s
    # def __str__(self):
        # return (f'ustatus: 0x{self.regs[0x00]}\n'
                # f'uie: 0x{self.regs[0x4 << 2]}\n')
    # def __str__(self):
        
        

    

def reset():
  global regfile, memory
  regfile = Regfile()
  # 16kb at 0x80000000
  memory = b'\x00'*0x4000

memory = b'\x00'*0x4000
regfile = Regfile()
csrs = CSregs()
PC = 32
logging.basicConfig(filename='summary.log', filemode='w', level=logging.INFO)

def ws(addr, dat):
  global memory
  #print(hex(addr), len(dat))
  addr -= 0x80000000
  assert addr >=0 and addr < len(memory)
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
        if i != 0 and i % 2 == 0:
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
    # Instruction Decodes
    ins_d = Decode(ins, regfile[PC])
    npc = 0x0

    logging.debug("PC: %x --- %s" % (regfile[PC], ins_d))

    if(ins_d.opcode == Ops.BRANCH):
        if (ins_d.resolve_branch(regfile[ins_d.rs1], regfile[ins_d.rs2])):
            npc = regfile[PC] + ins_d.imm_b
        else:
            npc = regfile[PC] + 4

    elif(ins_d.opcode == Ops.AUIPC):
        regfile[ins_d.rd] = regfile[PC] + ins_d.imm_u

    elif (ins_d.opcode == Ops.JALR):
        npc = (ins_d.imm_i + regfile[ins_d.rs1]) & 0xFFFFFFFE
        regfile[ins_d.rd] = regfile[PC] + 4

    elif (ins_d.opcode == Ops.JAL):
        regfile[1] = regfile[PC] + 4
        npc = (ins_d.imm_j) + regfile[PC]

    elif(ins_d.opcode == Ops.IMM):
        regfile[ins_d.rd] = Execute.ALU(ins_d.aluop_d, regfile[ins_d.rs1], ins_d.imm_i)

    elif(ins_d.opcode == Ops.OP):
        regfile[ins_d.rd] = Execute.ALU(ins_d.aluop_d, regfile[ins_d.rs1], regfile[ins_d.rs2])

    elif (ins_d.opcode == Ops.LOAD):
        insaddr = regfile[ins_d.rs1] + ins_d.imm_i
        if (ins_d.funct3 == Funct3.LW):
            regfile[ins_d.rd] = r32[insaddr]
        elif (ins_d.funct3 == Funct3.LH):
            regfile[ins_d.rd] = Utils.sign_extend(r32[insaddr] & 0xFFFF)
        elif (ins_d.funct3 == Funct3.LB):
            regfile[ins_d.rd] = Utils.sign_extend(r32[insaddr] & 0xFF)
        elif (ins_d.funct3 == Funct3.LHU):
            regfile[ins_d.rd] = r32[insaddr] & 0xFFFF
        elif (ins_d.funct3 == Funct3.LBU):
            regfile[ins_d.rd] = r32[insaddr] & 0xFF

    elif (ins_d.opcode == Ops.STORE):
        insaddr = regfile[ins_d.rs2] + ins_d.imm_s
        if (ins_d.funct3 == Funct3.SW):
            ws(regfile[ins_d.rs2] & 0xFFFFFFFF, insaddr)
        if (ins_d.funct3 == Funct3.SH):
            ws(regfile[ins_d.rs2] & 0xFFFF, insaddr)
        if (ins_d.funct3 == Funct3.SB):
            ws(regfile[ins_d.rs2]& 0xFF, insaddr)


    elif(ins_d.opcode == Ops.MISC):
        #Right now this can just be pass- coherence related
        pass

    elif(ins_d.opcode == Ops.LUI):
        regfile[ins_d.rd] = ins_d.imm_u


    elif(ins_d.opcode == Ops.SYSTEM):
        # CSRRW reads the old value of the CSR, zero-extends the value to XLEN bits,
        # then writes it to integer register rd. The initial value in rs1 is written to the CSR

        if ins_d.funct3 == Funct3.ECALL:
            if ins_d.funct3 == Funct3.ECALL:
                # print("  ecall", regfile[3])
                if regfile[3] > 1:
                    raise Exception("Failure in test %d" % regfile[3])
                elif regfile[3] == 1:
                    # tests passed successfully
                    return False
        
        # if ins_d.funct3 == Funct3.ADD:  #ECALL/EBREAK
        if ins_d.funct3 == Funct3.CSRRW: # read old csr value, zero extend to XLEN, write to rd. rs1 written to csr
            regfile[ins_d.rd] = csrs[ins_d.imm_i_unsigned]
            csrs[ins_d.imm_i_unsigned] = regfile[ins_d.rs1]

        if ins_d.funct3 == Funct3.CSRRS: # read, write to rd. rs1 is a bit mask corresponding to bit positions in the csr
            regfile[ins_d.rd] = csrs[ins_d.imm_i_unsigned]
            csrs[ins_d.imm_i_unsigned] = regfile[ins_d.rs1] | csrs[ins_d.imm_i_unsigned]

        if ins_d.funct3 == Funct3.CSRRC: # reads csr value, writes to rd. initial value treated as a bit mask 
            regfile[ins_d.rd] = csrs[ins_d.imm_i_unsigned]
            csrs[ins_d.imm_i_unsigned] = ~regfile[ins_d.rs1] & csrs[ins_d.imm_i_unsigned]
            
        if ins_d.funct3 == Funct3.CSRRWI: # if rd = x0 then do not read CSR, no side effects
            regfile[ins_d.rd] = csrs[ins_d.imm_i_unsigned]
            csrs[ins_d.imm_i_unsigned] = ins_d.rs1

        if ins_d.funct3 == Funct3.CSRRSI: # update csr with 5-bit unsigned immediate, no write to CSR
            regfile[ins_d.rd] = csrs[ins_d.imm_i_unsigned]
            csrs[ins_d.imm_i_unsigned] = ins_d.rs1 | csrs[ins_d.imm_i_unsigned]

        if ins_d.funct3 == Funct3.CSRRCI: # update csr with 5-bit unsigned immediate, no write to CSR
            regfile[ins_d.rd] = csrs[ins_d.imm_i_unsigned]
            csrs[ins_d.imm_i_unsigned] = ~ins_d.rs1 & csrs[ins_d.imm_i_unsigned]
            


        # regfile[ins_d.rd] = r32csr(ins_d.imm_i_unsigned)
        # wcsr(struct.pack("I", regfile[ins_d.rs1]), ins_d.imm_i_unsigned)
    else:
        dump()
        raise Exception("write op %x" % ins)

    regfile[PC] = Fetch.pc_sel(regfile[PC], npc, ins_d.opcode)


    return True


if __name__ == "__main__":
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    for x in glob.glob("riscv-tests/isa/rv32ui-p-*"):
        if x.endswith('.dump'):
            continue
        with open(x, 'rb') as f:
            reset()
            logging.debug("test %s", x)
            e = ELFFile(f)
            for s in e.iter_segments():
                ws(s.header.p_paddr, s.data())
            with open("test-cache/%s" % x.split("/")[-1], "wb") as g:
                g.write(b'\n'.join([binascii.hexlify(memory[i:i+4][::-1]) for i in range(0,len(memory),4)]))
                #g.write(b'\n'.join([binascii.hexlify(memory[i:i+1]) for i in range(0,len(memory))]))
            regfile[PC] = 0x80000000
            inscnt = 0
            while step():
                inscnt += 1
            logging.debug("  ran %d instructions" % inscnt)
            logging.debug(str(csrs))
        break
    dump()
