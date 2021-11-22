from enum import Enum, auto
import logging
import struct
from cpu_types import Ops, Utils


class PipelineStage():
    
    def __init__(self):
        logging.basicConfig(filename='summary.log', filemode='w', level=logging.DEBUG)

        self.ins            = -1
        self.pc             = 0x0
        self.npc            = 0x0
        self.use_npc        = False

        self.opcode         = Ops.NOP
        self.rd             = 0
        self.funct3         = Ops.JALR
        self.rs1            = 0
        self.rs2            = 0
        self.funct7         = 0
        self.imm_i          = 0
        self.imm_s          = 0
        self.imm_b          = 0
        self.imm_u          = 0
        self.imm_j          = 0
        self.imm_i_unsigned = 0
        self.opname         = 0
        self.aluop          = 0
        self.rdat1          = 0
        self.rdat2          = 0
        self.wdat           = 0
        self.wen            = 0
        self.ls_addr        = 0x0

        self.branch_target = 0xBAD1BAD1
        self.mispredict = False

    def update(self, prev):
        self.ins            = prev.ins
        self.pc             = prev.pc
        self.npc            = prev.npc
        self.use_npc        = prev.use_npc
        self.opcode         = prev.opcode
        self.rd             = prev.rd
        self.funct3         = prev.funct3
        self.rs1            = prev.rs1
        self.rs2            = prev.rs2
        self.funct7         = prev.funct7
        self.imm_i          = prev.imm_i
        self.imm_s          = prev.imm_s
        self.imm_b          = prev.imm_b
        self.imm_u          = prev.imm_u
        self.imm_j          = prev.imm_j
        self.imm_i_unsigned = prev.imm_i_unsigned
        self.opname         = prev.opname
        self.aluop          = prev.aluop
        self.rdat1          = prev.rdat1
        self.rdat2          = prev.rdat2
        self.wdat           = prev.wdat
        self.wen            = prev.wen
        self.ls_addr        = prev.ls_addr
        self.branch_target  = prev.branch_target
        self.mispredict     = prev.mispredict




    def __str__(self):
        # ins = "%x" % self.ins
        if self.opcode == Ops.IMM:
            return (f'0x{Utils.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rd}, '
                f'r{self.rs1}  '
                f'0x{Utils.gib(self.ins, 31, 20):x}'
                f'  @ PC ={Utils.zext(self.pc)} '
                )
        elif self.opcode == Ops.LUI:
            return (f'0x{Utils.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rd}, '
                f'    '
                f'0x{Utils.zext(self.imm_u)}'
                f'  @ PC ={Utils.zext(self.pc)} '
                )
        elif self.opcode == Ops.BRANCH:
            return (f'0x{Utils.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rs1}, '
                f'r{self.rs2} '
                f'0x{Utils.zext(self.imm_b, 4)}'
                f'  @ PC ={Utils.zext(self.pc)} '
                )
        elif self.opcode == Ops.SYSTEM:
            return (f'0x{Utils.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rs1}, '
                f'r{self.rs2} '
                f'0x{Utils.zext(self.imm_b, 4)}'
                f'  @ PC ={Utils.zext(self.pc)} '
                )
        else:
            return (f'0x{Utils.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rd}, '
                f'r{self.rs1}, '
                f'r{self.rs2}'
                f'  @ PC ={Utils.zext(self.pc)} '
                )