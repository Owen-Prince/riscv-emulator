#!/usr/bin/env python3
import glob
import os
import struct
import logging

from elftools.elf.elffile import ELFFile

from cpu_types import Funct3, Ops, Utils
from fetch_stage import InsFetch
from decode_stage import Decode
from execute_stage import Execute
from mem_stage import Memory
from wb_stage import Wb

mem = Memory()

ins_f = InsFetch(mem)
de = Decode()
ex = Execute()
wb = Wb()

class ElementCnt():
    def __init__(self):
        self.count = 0

logging.basicConfig(filename='summary.log', filemode='w', level=logging.INFO)


def step():
    '''
    Advance clock cycle
    '''

    global mem, de, ins_f, ex, wb
    # Instruction InsFetch
    ins = ins_f.fetch()
    ins_f.update(mem, 0x8000000, 0)
    ins_f.tick()
    logging.info("PC: %s --- %s" % (Utils.zext(ins_f.pc), Utils.zext(ins_f.ins)))
    logging.info("Input-Output: %s --- %s" % (Utils.zext(ins_f.ins), Utils.zext(ins_f.ins)))
    # de.update(ins, ins_f.pc)

    # # ex
    # # de.ins = ins
    # # Instruction Decodes
    # npc = 0x0


    # if(de.opcode == Ops.BRANCH):
    #     if (de.resolve_branch(de.regfile[de.rs1], de.regfile[de.rs2])):
    #         npc = de.pc + de.imm_b
    #     else:
    #         npc = de.pc + 4

    # elif(de.opcode == Ops.AUIPC):
    #     de.regfile[de.rd] = de.pc + de.imm_u

    # elif (de.opcode == Ops.JALR):
    #     npc = (de.imm_i + de.regfile[de.rs1]) & 0xFFFFFFFE
    #     de.regfile[de.rd] = de.pc + 4

    # elif (de.opcode == Ops.JAL):
    #     de.regfile[de.rd] = de.pc + 4
    #     npc = (de.imm_j) + de.pc

    # elif(de.opcode == Ops.IMM):
    #     de.regfile[de.rd] = ex.ALU(de.aluop_d, de.regfile[de.rs1], de.imm_i)

    # elif(de.opcode == Ops.OP):
    #     de.regfile[de.rd] = ex.ALU(de.aluop_d, de.regfile[de.rs1], de.regfile[de.rs2])

    # elif (de.opcode == Ops.LOAD):
    #     insaddr = de.regfile[de.rs1] + de.imm_i
    #     if (de.funct3 == Funct3.LW):
    #         de.regfile[de.rd] = mem[insaddr]
    #     elif (de.funct3 == Funct3.LH):
    #         de.regfile[de.rd] = Utils.sign_extend(mem[insaddr] & 0xFFFF)
    #     elif (de.funct3 == Funct3.LB):
    #         de.regfile[de.rd] = Utils.sign_extend(mem[insaddr] & 0xFF)
    #     elif (de.funct3 == Funct3.LHU):
    #         de.regfile[de.rd] = mem[insaddr] & 0xFFFF
    #     elif (de.funct3 == Funct3.LBU):
    #         de.regfile[de.rd] = mem[insaddr] & 0xFF

    # elif (de.opcode == Ops.STORE):
    #     insaddr = de.regfile[de.rs2] + de.imm_s
    #     if (de.funct3 == Funct3.SW):
    #         mem[insaddr] = de.regfile[de.rs2] & 0xFFFFFFFF
    #     if (de.funct3 == Funct3.SH):
    #         mem[insaddr] = de.regfile[de.rs2] & 0xFFFF
    #     if (de.funct3 == Funct3.SB):
    #         mem[insaddr] = de.regfile[de.rs2] & 0xFF


    # elif(de.opcode == Ops.MISC):
    #     #Right now this can just be pass- coherence related
    #     pass

    # elif(de.opcode == Ops.LUI):
    #     de.regfile[de.rd] = de.imm_u


    # elif(de.opcode == Ops.SYSTEM):
    #     # CSRRW reads the old value of the CSR, zero-extends the value to XLEN bits,
    #     # then writes it to integer register rd. The initial value in rs1 is written to the CSR

    #     if de.funct3 == Funct3.ECALL:
    #         if de.funct3 == Funct3.ECALL:
    #             # print("  ecall", de.regfile[3])
    #             if de.regfile[3] > 1:
    #                 # return False
    #                 raise Exception("Failure in test %x" % de.regfile[3])
    #             elif de.regfile[3] == 1:
    #                 # tests passed successfully
    #                 return False
        
    #     # if de.funct3 == Funct3.ADD:  #ECALL/EBREAK
    #     if de.funct3 == Funct3.CSRRW: # read old csr value, zero extend to XLEN, write to rd. rs1 written to csr
    #         de.regfile[de.rd] = mem.csrs[de.imm_i_unsigned]
    #         mem.csrs[de.imm_i_unsigned] = de.regfile[de.rs1]

    #     if de.funct3 == Funct3.CSRRS: # read, write to rd. rs1 is a bit mask corresponding to bit positions in the csr
    #         de.regfile[de.rd] = mem.csrs[de.imm_i_unsigned]
    #         mem.csrs[de.imm_i_unsigned] = de.regfile[de.rs1] | mem.csrs[de.imm_i_unsigned]

    #     if de.funct3 == Funct3.CSRRC: # reads csr value, writes to rd. initial value treated as a bit mask 
    #         de.regfile[de.rd] = mem.csrs[de.imm_i_unsigned]
    #         mem.csrs[de.imm_i_unsigned] = ~de.regfile[de.rs1] & mem.csrs[de.imm_i_unsigned]
            
    #     if de.funct3 == Funct3.CSRRWI: # if rd = x0 then do not read CSR, no side effects
    #         de.regfile[de.rd] = mem.csrs[de.imm_i_unsigned]
    #         mem.csrs[de.imm_i_unsigned] = de.rs1

    #     if de.funct3 == Funct3.CSRRSI: # update csr with 5-bit unsigned immediate, no write to CSR
    #         de.regfile[de.rd] = mem.csrs[de.imm_i_unsigned]
    #         mem.csrs[de.imm_i_unsigned] = de.rs1 | mem.csrs[de.imm_i_unsigned]

    #     if de.funct3 == Funct3.CSRRCI: # update csr with 5-bit unsigned immediate, no write to CSR
    #         de.regfile[de.rd] = mem.csrs[de.imm_i_unsigned]
    #         mem.csrs[de.imm_i_unsigned] = ~de.rs1 & mem.csrs[de.imm_i_unsigned]
            
    # else:
    #     raise Exception("write op %x" % ins)

    # ins_f.set_pc(npc, de.opcode, 0)
    # de.update_pc(ins_f.pc)


    return True


if __name__ == "__main__":
    # global mem
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    # for x in glob.glob("riscv-tests/isa/rv32ui-p-*"):
    x = "riscv-tests/isa/rv32ui-p-add"
    # if x.endswith('.dump'):
        # continue
    with open(x, 'rb') as f:
        mem.reset()
        de.reset()
        logging.info("test %s\n", x)
        e = ELFFile(f)
        for s in e.iter_segments():
            mem[s.header.p_paddr] = s.data()
        with open("test-cache/%s" % x.split("/")[-1], "wb") as g:
            mem.load(g)
        ins_f.input.pc = (0x80000000) 

        inscnt = 0
        # while step():
        while inscnt < 10:
            step()
            inscnt += 1
        logging.debug("  ran %d instructions" % inscnt)
        logging.debug(str(mem.csrs))
    print(de.regfile)
        # break
    # dump()
