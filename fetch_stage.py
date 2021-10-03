from os import stat
from cpu_types import Ops, Funct3, Aluop, Utils

class Fetch():
    @staticmethod
    def pc_sel(pc, npc, opcode):
        if opcode in [Ops.JALR, Ops.JAL, Ops.BRANCH]:
            return npc
        else:
            return pc + 4
