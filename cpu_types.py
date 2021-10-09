from enum import Enum, auto
# RV32I Base Instruction Set

class Ops(Enum):
    NOP = 0b0

    LUI = 0b0110111        # load upper immediate
    AUIPC = 0b0010111    # add upper immediate to pc

    JAL = 0b1101111
    JALR = 0b1100111

    BRANCH = 0b1100011

    LOAD = 0b0000011
    STORE = 0b0100011

    IMM = 0b0010011

    OP = 0b0110011

    MISC = 0b0001111 # FENCE, FENCE.I
    SYSTEM = 0b1110011 # CSRRW



class Funct3(Enum):
    JALR = 0b000

    BEQ  = 0b000
    BNE  = 0b001
    BLT  = 0b100
    BGE  = 0b101
    BLTU = 0b110
    BGEU = 0b111

    LB  = 0b000
    LH  = 0b001
    LW  = 0b010
    LBU = 0b100
    LHU = 0b101

    SB = 0b000
    SH = 0b001
    SW = 0b010

    SLLI = SLL = 0b001
    SRL = SRLI = SRA = SRAI = 0b101

    ADD = SUB = ADDI = 0b000
    SLT = SLTI = 0b010
    SLTU = SLTIU = 0b011

    XOR = XORI = 0b100
    OR = ORI = 0b110
    AND = ANDI = 0b111

    ECALL = 0b000
    CSRRW   = 0b001
    CSRRS   = 0b010
    CSRRC   = 0b011
    CSRRWI  = 0b101
    CSRRSI  = 0b110
    CSRRCI  = 0b111

class Aluop(Enum):
    ADD = auto()
    SUB = auto()

    SLL = auto()
    SRL = auto()
    SRA = auto()

    SLT = auto()
    SLTU = auto()

    XOR = auto()
    OR = auto()
    AND = auto()

class Utils():
    @staticmethod
    def zext(s, w=8):
        if (len(("%x" % s)) < w):
            return ("%x" % s).zfill(w)
        else:
            return ("%x" % s)

    @staticmethod
    def unsigned(x, l=32):
        if (x < 0):
        # if (x >> 31) & 0x1 == 1:
        # if Utils.gib(x, l, l-1) == 1:
            return -1*int((x ^ (0xFFFFFFFF >> (32 - l))) + 1)
        else:
            return x

    @staticmethod
    def sign_extend( x, l):
        if x >> (l-1) == 1:
            return -((1 << l) - x)
        else:
            return x

    @staticmethod
    def get_aluop_d(funct3, funct7):
        """map funct3 and funct7 to aluop control signal"""
        if funct3 == Funct3.ADD:
            return Aluop.ADD if (funct7 == 0) else Aluop.SUB
        elif funct3 == Funct3.SLL:
            return Aluop.SLL
        elif funct3 == Funct3.SRL:
            return Aluop.SRL if (funct7 == 0) else Aluop.SRA
        elif funct3 == Funct3.SLT:
            return Aluop.SLT
        elif funct3 == Funct3.SLTU:
            return Aluop.SLTU
        elif funct3 == Funct3.XOR:
            return Aluop.XOR
        elif funct3 == Funct3.OR:
            return Aluop.OR
        elif funct3 == Funct3.AND:
            return Aluop.AND
        else:
            raise Exception("Invalid Aluop %s" % funct3)

    @staticmethod
    def get_opname(op, f3):
        opname_dict = {
            (Ops.NOP, Funct3.JALR) : "NOP",
            (Ops.LUI, Funct3.ADD) : "LUI",
            (Ops.AUIPC, Funct3.ADD): "AUIPC",
            (Ops.JAL, Funct3.ADD) : "JAL",
            (Ops.JALR, Funct3.JALR) : "JALR",

            (Ops.BRANCH, Funct3.BEQ) : "BEQ",
            (Ops.BRANCH, Funct3.BNE) : "BNE",
            (Ops.BRANCH, Funct3.BLT) : "BLT",
            (Ops.BRANCH, Funct3.BGE) : "BGE",
            (Ops.BRANCH, Funct3.BLTU) : "BLTU",
            (Ops.BRANCH, Funct3.BGEU) : "BGEU",

            (Ops.LOAD, Funct3.LB) : "LB",
            (Ops.LOAD, Funct3.LH) : "LH",
            (Ops.LOAD, Funct3.LW) : "LW",
            (Ops.LOAD, Funct3.LBU) : "LBU",
            (Ops.LOAD, Funct3.LHU) : "LHU",

            (Ops.STORE, Funct3.SB) : "SB",
            (Ops.STORE, Funct3.SH) : "SH",
            (Ops.STORE, Funct3.SW) : "SW",

            (Ops.IMM, Funct3.ADDI) : "ADDI",
            (Ops.IMM, Funct3.SLTI) : "SLTI",
            (Ops.IMM, Funct3.SLTIU) : "SLTIU",
            (Ops.IMM, Funct3.XORI) : "XORI",
            (Ops.IMM, Funct3.ORI) : "ORI",
            (Ops.IMM, Funct3.ANDI) : "ANDI",
            (Ops.IMM, Funct3.SLLI) : "SLLI",
            (Ops.IMM, Funct3.SRLI) : "SRLI",
            (Ops.IMM, Funct3.SRAI) : "SRAI",
            (Ops.OP, Funct3.ADD) : "ADD",
            (Ops.OP, Funct3.SUB) : "SUB",
            (Ops.OP, Funct3.SLL) : "SLL",
            (Ops.OP, Funct3.SLT) : "SLT",
            (Ops.OP, Funct3.SLTU) : "SLTU",
            (Ops.OP, Funct3.XOR) : "XOR",
            (Ops.OP, Funct3.SRL) : "SRL",
            (Ops.OP, Funct3.SRA) : "SRA",
            (Ops.OP, Funct3.OR) : "OR",
            (Ops.OP, Funct3.AND) : "AND",

            (Ops.MISC, Funct3.ADD) : "FENCE",

            (Ops.SYSTEM, Funct3.ADD) : "ECALL/EBREAK",
            (Ops.SYSTEM, Funct3.CSRRW)  : "CSRRW",
            (Ops.SYSTEM, Funct3.CSRRS)  : "CSRRS",
            (Ops.SYSTEM, Funct3.CSRRC)  : "CSRRC",
            (Ops.SYSTEM, Funct3.CSRRWI) : "CSRRWI",
            (Ops.SYSTEM, Funct3.CSRRSI) : "CSRRSI",
            (Ops.SYSTEM, Funct3.CSRRCI) : "CSRRCI"
        }
        return opname_dict[(op, f3)]


    @staticmethod
    def gib(x, s, e):
        """ # x[s:e]"""
        return (x >> e) & ((1 << (s - e + 1))-1)

    def gibi(self, s, e):
        return (self.ins >> e) & ((1 << (s - e + 1))-1)

class Instr():
    def __init__(self, instruction):
        pass
