from cpu_types import Ops, Funct3, opname

class Decode():
    ins = 0b0
    ins = 0b0
    opcode = 0b0
    rd = 0b0
    funct3 = 0b0
    rs1 = 0b0
    rs2 = 0b0
    funct7 = 0b0


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

    def __str__(self):
        ins = "%x" % self.ins
        return (f'0x{ins.zfill(8)} - '
                f'{opname[(Ops(self.opcode), Funct3(self.funct3))]:6} '
                f'r{self.rd}, '
                f'r{self.rs1}, '
                f'r{self.rs2}'
                )

    def gibi(self, s, e):
        return (self.ins >> e) & ((1 << (s - e + 1))-1)

    def sign_extend(self, x, l):
        if x >> (l-1) == 1:
            return -((1 << l) - x)
        else:
            return x

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
            return (self.unsigned(rdat1) < self.unsigned(rdat2))
        elif (self.funct3 == Funct3.BGEU):
            return self.unsigned(rdat1) >= self.unsigned(rdat2)

    def unsigned(self, x):
        if (x >> 31) & 0x1 == 1:
            return (x ^ 0xFFFFFFFF) + 1
        else:
            return x
