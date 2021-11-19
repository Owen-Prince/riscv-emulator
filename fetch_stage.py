import struct
from os import stat
import logging
import binascii

from cpu_types import Aluop, Funct3, Ops, Utils
from pipeline_stages import decode_execute, fetch_decode,  PipelineStage


class InsFetch(PipelineStage):

    def __init__(self, mem, pc=0x80000000):
        self.input = fetch_decode()
        self.output = decode_execute()

        self.mem = mem
        self.pc = pc
        self.ins = 0x0
        self.branch_target = 0xBAD1BAD1
        self.mispredict = False
        

    def fetch(self):
        logging.debug("pc: %x", self.pc)
        ins = self.mem[self.pc]
        self.opcode = Ops(Utils.gib(ins, 6, 0))
        self.branch_target = Utils.sign_extend(Utils.gib(self.ins, 15, 0), 16)
        logging.debug("branch target: %s", self.branch_target)
        # self.funct3 = Funct3(Utils.gib(ins, 14, 12))
        # self.rs1    = Utils.gib(ins, 19, 15)
        # self.rs2    = Utils.gib(ins, 24, 20)

        return ins 

    def tick(self, stall=0, flush=0):
        self.pc = self.set_pc()
        self.ins = self.fetch()
        # self.ins = 

    def update(self, mem, correct_branch_target, mispredict):
        self.branch_target = correct_branch_target
        self.mispredict = mispredict

        # if (stall): return
        

    def set_pc(self, opcode=0, stall=0):
        if stall == True:
            return
        if self.mispredict:
            return self.branch_target
        elif opcode in [Ops.JALR, Ops.JAL]:
            return  #TODO
        elif opcode == Ops.BRANCH:
            return self.predict_branch_target()
        else:
            return  self.pc + 4

    def predict_branch_target(self):
        return self.pc + 4
