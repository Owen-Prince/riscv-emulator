import logging
from os import stat

from cpu_types import Aluop, Funct3, Ops, Utils

logging.basicConfig(filename='summary.log', filemode='w', level=logging.INFO)

class Decode(Utils):
    """
    opcode
    rd
    funct3
    rs1
    rs2
    funct7

    imm_i -> 12b for i type, JALR, load
    imm_i_unsigned: ^
    imm_s -> 12b for stores
    imm_b -> 12b for branches
    imm_u -> normal 20b for LUI and AUIPC
    imm_j -> weird 20b for j and jal

    aluop_d
    """
    def __init__(self, ins=0x0, pc=0x0):
        self.ins = ins
        self.pc = pc
        self.regfile = Regfile()

        self.split()

    def split(self):
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
                f'{self.opname:6} '
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
        elif self.opcode == Ops.SYSTEM:
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

    def update(self, ins, pc):
        self.ins = ins
        self.pc = pc
        self.split()

    def tick():
        pass

    def update_pc(self, pc):
        # self.regfile[PC] = pc
        self.pc = pc

    def update_ins(self, ins):
        self.ins = ins
        self.split()

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

    def reset(self):
        self.regs = Regfile()


class Regfile:

    def __init__(self):
        self.regs = [0x0]
    def __getitem__(self, key):
        return self.regs[key]
    def __setitem__(self, key, value):
        if key == 0:
            return
        self.regs[key] = value & 0xFFFFFFFF
        logging.error(self.regs[key])
        logging.debug("reg %d should be %x --- actual: %x ", key, value, self.regs[key])
    def __str__(self):
        pp = []
        for i in range(32):
            if i != 0 and i % 8 == 0:
                pp += "\n"
            pp += " %3s: %08x" % ("x%d" % i, self.regs[i])
        # pp += "\n    PC: %08x" % pc
        return ''.join(pp)
