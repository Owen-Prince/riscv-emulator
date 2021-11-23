import logging
from cpu_types import Funct3, Ops, Utils, Aluop
from PipelineStage import PipelineStage

class Execute(PipelineStage):

    def __init__(self):
        super().__init__()

        self.aluop    = 0
        self.rdat1    = 0
        self.rdat2    = 0
        self.rs1      = 0
        self.rs2      = 0
        self.wdat     = 0
        self.wen      = 0
        self.opcode   = 0
        self.ls_addr  = 0
        self.rd       = 0

    def update(self, de):
        super().update(de)
        self.aluop   = de.aluop
        self.rdat1   = de.rdat1
        self.rdat2   = de.rdat2
        self.rs1     = de.rs1
        self.rs2     = de.rs2
        self.opcode  = de.opcode
        self.ls_addr = de.ls_addr
        self.rd      = de.rd
        self.wen     = de.wen
        self.wdat    = de.wdat
        print(f"Execute - {self.wen} - Regfile[{self.rd}] = {self.wdat}")

        logging.info("EXECUTE:   %s", self)

    def tick(self):
        if self.ins == -1: return
        if (self.opcode == Ops.IMM):
            self.wdat = self.ALU(self.aluop, self.rdat1, self.rdat2)
                


    @staticmethod
    def ALU(aluop, a, b):
        if  (aluop == Aluop.ADD):  return a + b
        elif(aluop == Aluop.SUB):  return a - b

        elif(aluop == Aluop.SLL):  return a << (b & 0x1F)
        elif(aluop == Aluop.SRL):  return a >> (b & 0x1F)
        elif(aluop == Aluop.SRA):  return ((a & 0x7FFFFFFF) >> (b & 0x1F)) | (a & 0x80000000)

        elif(aluop == Aluop.SLT):  return 1 if (a < b) else 0
        elif(aluop == Aluop.SLTU): return 1 if (Utils.unsigned(a) < Utils.unsigned(b)) else 0

        elif(aluop == Aluop.XOR):  return a ^ b
        elif(aluop == Aluop.OR):   return a | b
        elif(aluop == Aluop.AND):  return a & b

        else:
            raise Exception("alu op %s" % Funct3(aluop))

    

    