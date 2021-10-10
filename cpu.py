#!/usr/bin/env python3
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

# regfile = [0]*33

fetch = Fetch()
decode = Decode()
execute = Execute()
mem = Mem()
wb = Wb()

class ElementCnt():
    def __init__(self):
        self.count = 0

PC = 32
logging.basicConfig(filename='summary.log', filemode='w', level=logging.INFO)



def dump():
    pass



def step():
    '''
    Advance clock cycle
    '''

    global mem, decode
    # Instruction Fetch
    ins = mem.r32(decode.pc)
    decode.update_ins(ins)
    # decode.ins = ins
    # Instruction Decodes
    npc = 0x0

    logging.info("PC: %x --- %s" % (decode.pc, decode))

    if(decode.opcode == Ops.BRANCH):
        if (decode.resolve_branch(decode.regfile[decode.rs1], decode.regfile[decode.rs2])):
            npc = decode.pc + decode.imm_b
        else:
            npc = decode.pc + 4

    elif(decode.opcode == Ops.AUIPC):
        decode.regfile[decode.rd] = decode.pc + decode.imm_u

    elif (decode.opcode == Ops.JALR):
        npc = (decode.imm_i + decode.regfile[decode.rs1]) & 0xFFFFFFFE
        decode.regfile[decode.rd] = decode.pc + 4

    elif (decode.opcode == Ops.JAL):
        decode.regfile[decode.rd] = decode.pc + 4
        npc = (decode.imm_j) + decode.pc

    elif(decode.opcode == Ops.IMM):
        decode.regfile[decode.rd] = Execute.ALU(decode.aluop_d, decode.regfile[decode.rs1], decode.imm_i)

    elif(decode.opcode == Ops.OP):
        decode.regfile[decode.rd] = Execute.ALU(decode.aluop_d, decode.regfile[decode.rs1], decode.regfile[decode.rs2])

    elif (decode.opcode == Ops.LOAD):
        insaddr = decode.regfile[decode.rs1] + decode.imm_i
        if (decode.funct3 == Funct3.LW):
            decode.regfile[decode.rd] = mem.r32[insaddr]
        elif (decode.funct3 == Funct3.LH):
            decode.regfile[decode.rd] = Utils.sign_extend(mem.r32[insaddr] & 0xFFFF)
        elif (decode.funct3 == Funct3.LB):
            decode.regfile[decode.rd] = Utils.sign_extend(mem.r32[insaddr] & 0xFF)
        elif (decode.funct3 == Funct3.LHU):
            decode.regfile[decode.rd] = mem.r32[insaddr] & 0xFFFF
        elif (decode.funct3 == Funct3.LBU):
            decode.regfile[decode.rd] = mem.r32[insaddr] & 0xFF

    elif (decode.opcode == Ops.STORE):
        insaddr = decode.regfile[decode.rs2] + decode.imm_s
        if (decode.funct3 == Funct3.SW):
            mem.ws(decode.regfile[decode.rs2] & 0xFFFFFFFF, insaddr)
        if (decode.funct3 == Funct3.SH):
            mem.ws(decode.regfile[decode.rs2] & 0xFFFF, insaddr)
        if (decode.funct3 == Funct3.SB):
            mem.ws(decode.regfile[decode.rs2]& 0xFF, insaddr)


    elif(decode.opcode == Ops.MISC):
        #Right now this can just be pass- coherence related
        pass

    elif(decode.opcode == Ops.LUI):
        decode.regfile[decode.rd] = decode.imm_u


    elif(decode.opcode == Ops.SYSTEM):
        # CSRRW reads the old value of the CSR, zero-extends the value to XLEN bits,
        # then writes it to integer register rd. The initial value in rs1 is written to the CSR

        if decode.funct3 == Funct3.ECALL:
            if decode.funct3 == Funct3.ECALL:
                # print("  ecall", decode.regfile[3])
                if decode.regfile[3] > 1:
                    # return False
                    raise Exception("Failure in test %x" % decode.regfile[3])
                elif decode.regfile[3] == 1:
                    # tests passed successfully
                    return False
        
        # if decode.funct3 == Funct3.ADD:  #ECALL/EBREAK
        if decode.funct3 == Funct3.CSRRW: # read old csr value, zero extend to XLEN, write to rd. rs1 written to csr
            decode.regfile[decode.rd] = mem.csrs[decode.imm_i_unsigned]
            mem.csrs[decode.imm_i_unsigned] = decode.regfile[decode.rs1]

        if decode.funct3 == Funct3.CSRRS: # read, write to rd. rs1 is a bit mask corresponding to bit positions in the csr
            decode.regfile[decode.rd] = mem.csrs[decode.imm_i_unsigned]
            mem.csrs[decode.imm_i_unsigned] = decode.regfile[decode.rs1] | mem.csrs[decode.imm_i_unsigned]

        if decode.funct3 == Funct3.CSRRC: # reads csr value, writes to rd. initial value treated as a bit mask 
            decode.regfile[decode.rd] = mem.csrs[decode.imm_i_unsigned]
            mem.csrs[decode.imm_i_unsigned] = ~decode.regfile[decode.rs1] & mem.csrs[decode.imm_i_unsigned]
            
        if decode.funct3 == Funct3.CSRRWI: # if rd = x0 then do not read CSR, no side effects
            decode.regfile[decode.rd] = mem.csrs[decode.imm_i_unsigned]
            mem.csrs[decode.imm_i_unsigned] = decode.rs1

        if decode.funct3 == Funct3.CSRRSI: # update csr with 5-bit unsigned immediate, no write to CSR
            decode.regfile[decode.rd] = mem.csrs[decode.imm_i_unsigned]
            mem.csrs[decode.imm_i_unsigned] = decode.rs1 | mem.csrs[decode.imm_i_unsigned]

        if decode.funct3 == Funct3.CSRRCI: # update csr with 5-bit unsigned immediate, no write to CSR
            decode.regfile[decode.rd] = mem.csrs[decode.imm_i_unsigned]
            mem.csrs[decode.imm_i_unsigned] = ~decode.rs1 & mem.csrs[decode.imm_i_unsigned]
            
    else:
        dump()
        raise Exception("write op %x" % ins)

    decode.update_pc( Fetch.pc_sel(decode.pc, npc, decode.opcode))


    return True


if __name__ == "__main__":
    # global mem
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    for x in glob.glob("riscv-tests/isa/rv32ui-p-*"):
        if x.endswith('.dump'):
            continue
        with open(x, 'rb') as f:
            mem.reset()
            decode.reset()
            logging.info("test %s", x)
            e = ELFFile(f)
            for s in e.iter_segments():
                mem.ws(s.header.p_paddr, s.data())
            with open("test-cache/%s" % x.split("/")[-1], "wb") as g:
                mem.load(g)
            decode.update_pc(0x80000000) 
            inscnt = 0
            while step():
                inscnt += 1
                # if inscnt > 5:
                    # break
            logging.debug("  ran %d instructions" % inscnt)
            logging.debug(str(mem.csrs))
            logging.debug(decode.regfile)
        # break
    # dump()
