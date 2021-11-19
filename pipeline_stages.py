from enum import Enum, auto
import struct
from cpu_types import Utils


class PipelineStage():
    def __init__(self):
        self.input = None
        self.output = None
        self.stall = None
        self.flush = None

    def tick(self):
        if (self.flush):
            self.out = 0
            return
        elif (self.stall):
            return
        else:
            self.out = self.input

class fetch_decode(PipelineStage):
    def __init__(self):
        self.mem = None
        self.pc = None
        self.ins = None
        self.branch_pc = None
        self.mispredict = None

class decode_execute(PipelineStage):
    def __init__(self):
        self.ins = None
        self.pc = None
        self.opcode = None
        self.rd = None
        self.funct3 = None
        self.rs1 = None
        self.rs2 = None
        self.funct7 = None
        self.imm_i = None
        self.imm_s = None
        self.imm_b = None
        self.imm_u = None
        self.imm_j = None
        self.imm_i_unsigned = None
        self.opname = None
        self.aluop_d = None

class execute_mem(PipelineStage):
    def __init__(self):
        self.rdat1 = None
        self.rdat2 = None
        self.rd = None
        self.wen = None
        self.addr = None
        self.store_data = None
        self.result = None

class mem_writeback(PipelineStage):
    def __init__(self):
        self.load_data = None
        self.rd = None
        self.wen = None
        self.result = None

class writeback_decode(PipelineStage):
    def __init__(self):
        self.load_data = None
        self.rd = None
        self.wen = None
        self.result = None