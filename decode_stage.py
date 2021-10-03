from os import stat
from cpu_types import Ops, Funct3, Aluop, Utils

class Decode(Utils):

    def __init__(self, ins):
        self.ins = ins
        self.opcode = Ops(self.gibi(6, 0))
        self.rd     = self.gibi(11, 7)
        self.funct3 = Funct3(self.gibi(14, 12))
        self.rs1    = self.gibi(19, 15)
        self.rs2    = self.gibi(24, 20)
        self.funct7 = self.gibi(31, 25)

        self.imm_i = self.sign_extend(self.gibi(31, 20), 12)
        self.imm_s = self.sign_extend(self.gibi(11, 7) | (self.gibi(31, 25) << 5), 12)
        self.imm_b = self.sign_extend((self.gibi(11, 8) << 1) | (self.gibi(30, 25) << 5) | (self.gibi(8, 7) << 11) | (self.gibi(32, 31) << 12), 13)
        self.imm_u  = self.gibi(31, 12) << 12
        self.imm_j = self.sign_extend((self.gibi(30, 21) << 1) | (self.gibi(21, 20) << 11) | (self.gibi(19, 12) << 12) | (self.gibi(32, 31) << 20), 21)
        self.imm_i_unsigned = self.gibi(31, 20)

        self.opname = self.get_opname(self.opcode, self.funct3)
        self.aluop_d = self.get_aluop_d(self.funct3, self.funct7)


    def __str__(self):
        # ins = "%x" % self.ins
        if self.opcode == Ops.IMM:
            return (f'0x{self.zext(self.ins)} - '
                f'{opname:6} '
                f'r{self.rd}, '
                f'r{self.rs1}  '
                f'0x{self.gibi(31, 20):x}'
                )
        elif self.opcode == Ops.LUI:
            return (f'0x{self.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rd}, '
                f'    '
                f'0x{self.zext(self.imm_u)}'
                )
        elif self.opcode == Ops.BRANCH:
            return (f'0x{self.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rs1}, '
                f'r{self.rs2} '
                f'0x{self.zext(self.imm_b, 4)}'
                )
        else:
            return (f'0x{self.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rd}, '
                f'r{self.rs1}, '
                f'r{self.rs2}'
                )

    def resolve_branch(self, rdat1, rdat2):
        if (self.funct3 == Funct3.BEQ):
            return rdat1 == rdat2
        elif (self.funct3 == Funct3.BNE):
            return (rdat1 != rdat2)
        elif (self.funct3 == Funct3.BLT):
            return (rdat1 < rdat2)
        elif (self.funct3 == Funct3.BGE):
            return (rdat1 >= rdat2)
        elif (self.funct3 == Funct3.BLTU):
            return (Utils.unsigned(rdat1) < Utils.unsigned(rdat2))
        elif (self.funct3 == Funct3.BGEU):
            return Utils.unsigned(rdat1) >= Utils.unsigned(rdat2)
