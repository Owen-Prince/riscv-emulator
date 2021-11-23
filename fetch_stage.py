import struct
from os import stat
import logging
import binascii

from cpu_types import Aluop, Funct3, Ops, Utils
from PipelineStage import PipelineStage


class InsFetch(PipelineStage):

    def __init__(self, memory=None, pc=0x80000000):
        super().__init__()
        self.memory = memory
        self.pc = pc
        self.prev_pc = self.pc
        # self.ins = 0x0
        # self.branch_target = 0xBAD1BAD1
        self.npc = 0xBAD1BAD1
        self.use_npc = False
        self.de_op = Ops.NOP
        

    def fetch(self):
        logging.debug("pc: %x", self.pc)
        ins = self.memory[self.pc]
        self.opcode = Ops(Utils.gib(ins, 6, 0))
        self.jump_target = Utils.sign_extend(Utils.gib(self.ins, 15, 0), 16)
        # logging.info("branch target: %s", self.jump_target)
        # self.funct3 = Funct3(Utils.gib(ins, 14, 12))
        # self.rs1    = Utils.gib(ins, 19, 15)
        # self.rs2    = Utils.gib(ins, 24, 20)
        return ins 

    def update(self, memory, de):
        self.npc = de.npc
        self.use_npc = de.use_npc
        # self.memory = self.memory
        logging.info("FETCH:     %s", self)

    def tick(self, stall=0, flush=0):
        self.prev_pc = self.pc
        if (self.use_npc): 
            self.ins = self.fetch()
            self.pc = self.npc 
        else:
            self.ins = self.fetch()
            self.pc = self.set_pc()

        # self.ins = 
        

    def set_pc(self, opcode=0, stall=0):
        if stall == True:
            return
        if self.use_npc:
            return self.npc
        # elif opcode in [Ops.JALR, Ops.JAL]:
            # return  #TODO
        elif opcode == Ops.BRANCH:
            return self.predict_branch_target()
        else:
            return  self.pc + 4

    def predict_branch_target(self):
        return self.pc + 4

    def __str__(self):
        return (f'0x{Utils.zext(self.ins)} '
        f'@ PC ={Utils.zext(self.pc)} '
        )
