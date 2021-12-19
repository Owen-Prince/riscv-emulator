from cpu_types import Fail, Funct3, Ops, Success, get_aluop_d, get_opname, gib, sign_extend, unsigned

class Instruction:
    def __init__(self, ins_hex, regs=None):
        appx = lambda x : 'x' + str(x) 
        app0x = lambda x : '0x' + str(x) if int(x) >= 0 else '-0x' + str(-1 * x)
        if (ins_hex == -1): return
        # if (gib(ins_hex, 6, 0) not in list(Ops)): print("ERROR: %s", ins_hex)
        self.opcode = Ops(gib(ins_hex, 6, 0))
        self.rd     = gib(ins_hex, 11, 7)
        self.funct3 = Funct3(gib(ins_hex, 14, 12))
        self.funct7 = gib(ins_hex, 31, 25)

        self.rs1    = gib(ins_hex, 19, 15)
        self.rs2    = gib(ins_hex, 24, 20)

        self.imm_i = sign_extend(gib(ins_hex, 31, 20), 12)
        self.imm_s = sign_extend(gib(ins_hex, 11, 7) |
                                (gib(ins_hex, 31, 25) << 5), 12)
        self.imm_b = sign_extend((gib(ins_hex, 11, 8) << 1) |
                                (gib(ins_hex, 30, 25) << 5) |
                                (gib(ins_hex, 8, 7) << 11) |
                                (gib(ins_hex, 32, 31) << 12), 13)
        self.imm_u = gib(ins_hex, 31, 12) << 12
        self.imm_j = sign_extend((gib(ins_hex, 30, 21) << 1) |
                                (gib(ins_hex, 21, 20) << 11) |
                                (gib(ins_hex, 19, 12) << 12) |
                                (gib(ins_hex, 32, 31) << 20), 21)
        self.imm_i_unsigned = gib(ins_hex, 31, 20)

        self.opname = get_opname(self.opcode, self.funct3)
        self.aluop  = get_aluop_d(self.funct3, self.funct7)

        if regs is None:
            # print("regs are none")
            self.rdat1  = 0
            self.rdat2  = 0
        else:
            self.rdat1  = regs[self.rs1]
            self.rdat2  = regs[self.rs2]
        self.wdat           = 0xBAD0BAD0
        self.wen            = False
        self.ls_addr        = 0x0

        self.as_str = {}
        self.as_str[Ops.IMM]    = f'{self.opname:6}{appx(self.rd):>3}, {appx(self.rs1):>3}  {app0x(self.imm_i_unsigned):<12}'
        self.as_str[Ops.LUI]    = f'{self.opname:6}{appx(self.rd):>3},      {app0x(self.imm_u):>12}'
        self.as_str[Ops.BRANCH] = f'{self.opname:6}{appx(self.rs1):>3}, {appx(self.rs2):>3}  {app0x(self.imm_b):<12}'
        self.as_str[Ops.SYSTEM] = f'{self.opname:6}{appx(self.rs1):>3}, {appx(self.rs2):>3}  {app0x(self.imm_b):<12}'
        self.as_str_default     = f'{self.opname:6}{appx(self.rd):>3}, {appx(self.rs1):>3}, {appx(self.rs2):<12}'
        self.use_npc = False
        self.npc = 0x0
        self.regs = regs
        self.ins_hex = ins_hex

    def __str__(self):
        if self.opcode not in self.as_str.keys():
            return self.as_str_default
        return self.as_str[self.opcode]

    def set_imm(self, ins_hex):
        imm = {}
        imm['i']  = sign_extend(gib(ins_hex, 31, 20), 12)
        imm['s']  = sign_extend(gib(ins_hex, 11, 7) | (gib(ins_hex, 31, 25) << 5), 12)
        imm['b']  = sign_extend((gib(ins_hex, 11, 8) << 1) | (gib(ins_hex, 30, 25) << 5) | (gib(ins_hex, 8, 7) << 11) | (gib(ins_hex, 32, 31) << 12), 13)
        imm['u']  = gib(ins_hex, 31, 12) << 12
        imm['j']  = sign_extend((gib(ins_hex, 30, 21) << 1) | (gib(ins_hex, 21, 20) << 11) | (gib(ins_hex, 19, 12) << 12) | (gib(ins_hex, 32, 31) << 20), 21)
        imm['iu'] = gib(ins_hex, 31, 20)
        return imm


    def set_control_signals(self, pc):
        if (self.opcode == Ops.NOP):
            return

        self.wen = self.opcode in [Ops.IMM, Ops.AUIPC, Ops.JALR, Ops.JAL, Ops.LOAD, Ops.LUI, Ops.OP]
        self.use_npc = self.opcode in [Ops.JALR, Ops.JAL]
            # self.use_npc = True
        # elif (self.opcode == Ops.BRANCH) and self.is_correct_prediction(self.rdat1, self.rdat2):
        #     self.use_npc = True
        #     self.npc = pc + self.imm_b

        # self.use_npc = self.opcode in [Ops.JALR, Ops.JAL] or (self.opcode == Ops.BRANCH and not self.is_correct_prediction(self.rdat1, self.rdat2))

        if(self.opcode == Ops.BRANCH):
            if (self.take_branch(self.rdat1, self.rdat2)):
                self.npc = pc + self.imm_b
                self.use_npc = True
                print(f'{self.imm_b} {pc:x}')
            # else:
                # self.npc = pc + 4
        elif (self.opcode == Ops.IMM):
            # self.wen = True                     ###
            pass
        elif(self.opcode == Ops.AUIPC):
            self.wdat = pc + self.imm_u
            # self.wen = True                     ###

        elif (self.opcode == Ops.JALR):
            self.npc = (self.imm_i + self.rdat1 + 4) & 0xFFFFFFFE
            self.wdat = pc + 4
            # self.wen = True
            self.use_npc = True


        elif (self.opcode == Ops.JAL):
            self.wdat = pc + 4
            self.npc = (self.imm_j) + pc
            # self.wen = True
            self.use_npc = True


        elif (self.opcode == Ops.LOAD):
            self.ls_addr = self.rdat1 + self.imm_i
            # self.wsel = 
            # self.wen = True

        elif (self.opcode == Ops.STORE):
            self.ls_addr = self.rdat1 + self.imm_s
            if (self.funct3 == Funct3.SW):
                self.wdat = self.rdat2 & 0xFFFFFFFF
            if (self.funct3 == Funct3.SH):
                self.wdat = self.rdat2 & 0xFFFF
            if (self.funct3 == Funct3.SB):
                self.wdat = self.rdat2 & 0xFF
            self.wen = False

        elif(self.opcode == Ops.MISC):
            self.wen = False
        #Right now this can just be pass- coherence related

        elif(self.opcode == Ops.LUI):
            # self.wen = True
            self.wdat = self.imm_u


        elif(self.opcode == Ops.SYSTEM):
            self.wen = False
        # CSRRW reads the old value of the CSR, zero-extends the value to XLEN bits,
        # then writes it to integer register rd. The initial value in rs1 is written to the CSR
            if self.funct3 == Funct3.ECALL:
                # if self.funct3 == Funct3.ECALL:
                    #These 2 lines are used for testing with the riscv-tests repository
                if self.imm_i_unsigned == 302:
                    pass
                # elif self.regs[3] > 1:
                elif self.regs[3] != 1:
                    raise Fail("Failure in test %x" % self.regs[3])
                elif self.regs[3] == 1:
                    print("SUCCESS")
                    raise Success("Success")
                    # tests passed successfully

            # self.csr_addr = self.imm_i_unsigned
        else:
            pass
           
    def take_branch(self, rdat1, rdat2, predicted=False) -> bool:
        """
        if True take the branch.
        Since the branch is currently predicted to be always 
        not taken, if the branch condition evaluates to True
        then this function will return True
        """
        if (self.funct3 == Funct3.BEQ):
            return (rdat1 == rdat2)
        elif (self.funct3 == Funct3.BNE):
            return (rdat1 != rdat2) 
        elif (self.funct3 == Funct3.BLT):
            return (rdat1 < rdat2) 
        elif (self.funct3 == Funct3.BGE):
            return (rdat1 >= rdat2) 
        elif (self.funct3 == Funct3.BLTU):
            return (unsigned(rdat1) < unsigned(rdat2)) 
        elif (self.funct3 == Funct3.BGEU):
            return (unsigned(rdat1) >= unsigned(rdat2)) 