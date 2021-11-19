import logging
from os import stat

from cpu_types import Aluop, Funct3, Ops, Utils
from pipeline_stages import PipelineStage

logging.basicConfig(filename='summary.log', filemode='w', level=logging.INFO)

class Regfile:

    def __init__(self):
        self.regs = [0x0]*32 
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
class Decode(PipelineStage):
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
        self.branch_target = 0x0
        self.mispredict = False
        self.split()

    def split(self):
        self.opcode = Ops(Utils.gib(self.ins, 6, 0))
        self.rd     = Utils.gib(self.ins, 11, 7)
        self.funct3 = Funct3(Utils.gib(self.ins, 14, 12))
        self.rs1    = Utils.gib(self.ins, 19, 15)
        self.rs2    = Utils.gib(self.ins, 24, 20)
        self.funct7 = Utils.gib(self.ins, 31, 25)

        self.imm_i = Utils.sign_extend(Utils.gib(self.ins, 31, 20), 12)
        self.imm_s = Utils.sign_extend(Utils.gib(self.ins, 11, 7) | (Utils.gib(self.ins, 31, 25) << 5), 12)
        self.imm_b = Utils.sign_extend((Utils.gib(self.ins, 11, 8) << 1) | (Utils.gib(self.ins, 30, 25) << 5) | (Utils.gib(self.ins, 8, 7) << 11) | (Utils.gib(self.ins, 32, 31) << 12), 13)
        self.imm_u  = Utils.gib(self.ins, 31, 12) << 12
        self.imm_j = Utils.sign_extend((Utils.gib(self.ins, 30, 21) << 1) | (Utils.gib(self.ins, 21, 20) << 11) | (Utils.gib(self.ins, 19, 12) << 12) | (Utils.gib(self.ins, 32, 31) << 20), 21)
        self.imm_i_unsigned = Utils.gib(self.ins, 31, 20)

        self.opname = Utils.get_opname(self.opcode, self.funct3)
        self.aluop_d = Utils.get_aluop_d(self.funct3, self.funct7)






    def __str__(self):
        # ins = "%x" % self.ins
        if self.opcode == Ops.IMM:
            return (f'0x{self.zext(self.ins)} - '
                f'{self.opname:6} '
                f'r{self.rd}, '
                f'r{self.rs1}  '
                f'0x{Utils.gib(self.ins, 31, 20):x}'
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
        self.rdat1 = self.regfile[self.rs1]
        self.rdat2 = self.regfile[self.rs1]
        


    def tick():
        pass

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



    def control(self):
        if(self.opcode == Ops.BRANCH):
            if (self.resolve_branch(self.regfile[self.rs1], self.regfile[self.rs2])):
                self.branch_target = self.pc + self.imm_b
                self.mispredict = True
            else:
                self.branch_target = self.pc + 4

        elif(self.opcode == Ops.AUIPC):
            self.wdata = self.pc + self.imm_u

        elif (self.opcode == Ops.JALR):
            npc = (self.imm_i + self.regfile[self.rs1]) & 0xFFFFFFFE
            self.regfile[self.rd] = self.pc + 4

        elif (self.opcode == Ops.JAL):
            self.regfile[self.rd] = self.pc + 4
            npc = (self.imm_j) + self.pc

        elif (self.opcode == Ops.LOAD):
            self.insaddr = self.regfile[self.rs1] + self.imm_i

        elif (self.opcode == Ops.STORE):
            insaddr = self.regfile[self.rs2] + self.imm_s
            if (self.funct3 == Funct3.SW):
                self.store_data = self.regfile[self.rs2] & 0xFFFFFFFF
            if (self.funct3 == Funct3.SH):
                self.store_data = self.regfile[self.rs2] & 0xFFFF
            if (self.funct3 == Funct3.SB):
                self.store_data = self.regfile[self.rs2] & 0xFF


        elif(self.opcode == Ops.MISC):
        #Right now this can just be pass- coherence related
            pass

        elif(self.opcode == Ops.LUI):
            self.wdata = self.imm_u


        elif(self.opcode == Ops.SYSTEM):
        # CSRRW reads the old value of the CSR, zero-extends the value to XLEN bits,
        # then writes it to integer register rd. The initial value in rs1 is written to the CSR

            if self.funct3 == Funct3.ECALL:
                if self.funct3 == Funct3.ECALL:
                    # print("  ecall", self.regfile[3])
                    if self.regfile[3] > 1:
                    # return False
                        raise Exception("Failure in test %x" % self.regfile[3])
                    elif self.regfile[3] == 1:
                    # tests passed successfully
                        return False
        
            # if self.funct3 == Funct3.ADD:  #ECALL/EBREAK
            # if self.funct3 in [Funct3.CSRRW, Funct3.CSRRS, Funct3.CSRRC, Funct3.CSRRWI, Funct3.CSRRSI, Funct3.CSRRCI]:

            if self.funct3 == Funct3.CSRRW: # read old csr value, zero extend to XLEN, write to rd. rs1 written to csr
                self.csrs[self.imm_i_unsigned] = self.regfile[self.rs1]
            elif self.funct3 == Funct3.CSRRS: # read, write to rd. rs1 is a bit mask corresponding to bit positions in the csr
                self.csrs[self.imm_i_unsigned] = self.regfile[self.rs1] | self.csrs[self.imm_i_unsigned]
            elif self.funct3 == Funct3.CSRRC: # reads csr value, writes to rd. initial value treated as a bit mask 
                self.csrs[self.imm_i_unsigned] = ~self.regfile[self.rs1] & self.csrs[self.imm_i_unsigned]
            elif self.funct3 == Funct3.CSRRWI: # if rd = x0 then do not read CSR, no side effects
                self.csrs[self.imm_i_unsigned] = self.rs1
            elif self.funct3 == Funct3.CSRRSI: # update csr with 5-bit unsigned immediate, no write to CSR
                self.csrs[self.imm_i_unsigned] = self.rs1 | self.csrs[self.imm_i_unsigned]
            elif self.funct3 == Funct3.CSRRCI: # update csr with 5-bit unsigned immediate, no write to CSR
                self.csrs[self.imm_i_unsigned] = ~self.rs1 & self.csrs[self.imm_i_unsigned]
            
        else:
            raise Exception("write op %x" % self.ins)