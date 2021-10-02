from enum import Enum, auto
# RV32I Base Instruction Set



class Ops(Enum):
    LUI = 0b0110111        # load upper immediate
    AUIPC = 0b0010111    # add upper immediate to pc

    JAL = 0b1101111
    JALR = 0b1100111

    BRANCH = 0b1100011

    LOAD = 0b0000011
    STORE = 0b0100011

    IMM = 0b0010011

    OP = 0b0110011

    MISC = 0b0001111
    SYSTEM = 0b1110011

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

    ADD = SUB = ADDI = 0b000
    SLLI = 0b001
    SLT = SLTI = 0b010
    SLTU = SLTIU = 0b011

    XOR = XORI = 0b100
    SRL = SRLI = SRA = SRAI = 0b101
    SLL = 0b001
    OR = ORI = 0b110
    AND = ANDI = 0b111

class Aluop(Enum):
    ADD = auto()
    SUB = auto()

opname = {
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
    (Ops.SYSTEM, Funct3.ADD) : "ECALL/EBREAK"
}
