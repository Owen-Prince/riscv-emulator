from cpu_types import Funct3, Ops, Utils, Aluop
from pipeline_stages import PipelineStage, decode_execute, execute_mem

class Execute(PipelineStage):

    def __init__(self):
        pass

    def update(self, de):
        self.aluop = de.aluop
        self.rdat1 = de.rdat1
        self.rdat2 = de.rdat2
        self.wdat  = de.wdat
        self.wen   = de.wen
        self.opcode = de.opcode
        self.ls_addr   = de.ls_addr
        self.rd = de.rd

    def tick(self):
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

    

    