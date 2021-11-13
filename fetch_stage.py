import struct
from os import stat
import logging

from cpu_types import Aluop, Funct3, Ops, Utils


class InsFetch():

    def __init__(self, mem, pc=0x80000000):
        self.mem = mem
        self.pc = pc
        self.ins = 0x0

    def fetch(self):
        logging.debug("pc: %x", self.pc)
        self.ins = self.mem[self.pc]
        return self.ins 

    def tick(self):
        pass
        # if (stall): return
        

    def set_pc(self, npc, opcode, stall):
        if stall == True:
            return
        elif opcode in [Ops.JALR, Ops.JAL, Ops.BRANCH]:
            self.pc = npc
        else:
            self.pc =  self.pc + 4
