import struct
import binascii

from elftools.elf.elffile import ELFFile

from cpu_types import Aluop, Funct3, Ops, get_aluop_d, get_opname, gib, pad, sign_extend, unsigned, zext

class Success(Exception):
    pass

class Ram():
    def __init__(self):
        self.memory = b'\x00'*0x4000

    def __getitem__(self, key):
        key -= 0x80000000
        if key < 0 or key >= len(self.memory):

            raise Exception("mem fetch to %x failed" % key)
        assert key >=0 and key < len(self.memory)
        return struct.unpack("<I", self.memory[key:key+4])[0]

    def __setitem__(self, key, val):
        key -= 0x80000000
        assert key >=0 and key < len(self.memory)

        self.memory = self.memory[:key] + val + self.memory[key+len(val):]

    def load(self, filename):
        self.reset()
        with open(filename, 'rb') as f:
            e = ELFFile(f)
            for s in e.iter_segments():
                # if s.data() != 0:
                    # print(s.data(), "\n")
                self[s.header.p_paddr] = s.data()
            with open("test-cache/%s" % filename.split("/")[-1], "wb") as g:
                g.write(b'\n'.join([binascii.hexlify(self.memory[i:i+4][::-1]) for i in range(0,len(self.memory),4)]))
    def reset(self):
        self.memory =  b'\x00'*0x4000

    def __str__(self):
        s = []
        bad = []
        for i in range(0, len(self.memory), 4):
            if self[i + 0x80000000] != 0:
                padded = pad(hex(self[i + 0x80000000])[2:])
                if len(padded) != 8: bad.append(hex(self[i + 0x80000000]))
                s.append(f"{hex(i)}:\t0x{padded}\n")
        return "".join(s)



class Regfile:
    def __init__(self):
        self.regs = [0x0]*32
    def __getitem__(self, key):
        return self.regs[key]
    def __setitem__(self, key, value):
        if key == 0:
            return
        self.regs[key] = value & 0xFFFFFFFF
        # logging.error(self.regs[key])
        # logging.debug("reg %d should be %x --- actual: %x ", key, value, self.regs[key])
    def __str__(self):
        s = []
        for i in range(32):
            s.append(f"{i}: {hex(self.regs[i])} \n")
        return "".join(s)

class Instruction:
    def __init__(self, ins_hex, regs=None):
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
            print("regs are none")
            self.rdat1  = 0
            self.rdat2  = 0
        else:
            self.rdat1  = regs[self.rs1]
            self.rdat2  = regs[self.rs2]
        self.wdat           = 0xBAD0BAD0
        self.wen            = False
        self.ls_addr        = 0x0

        self.as_str = {}
        self.as_str[Ops.IMM]    = f'{self.opname:6} x{self.rd}, x{self.rs1}  0x{self.imm_i_unsigned:>x}'
        self.as_str[Ops.LUI]    = f'{self.opname:6} x{self.rd}, 0x{zext(self.imm_u):>}'
        self.as_str[Ops.BRANCH] = f'{self.opname:6} x{self.rs1}, x{self.rs2} 0x{zext(self.imm_b, 4):>}'
        self.as_str[Ops.SYSTEM] = f'{self.opname:6} x{self.rs1}, x{self.rs2} 0x{zext(self.imm_b, 4):>}'
        self.as_str_default     = f'{self.opname:6} x{self.rd}, x{self.rs1}, x{self.rs2:>}'
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
        if self.opcode in [Ops.JALR, Ops.JAL]:
            self.use_npc = True
        elif (self.opcode == Ops.BRANCH) and self.is_correct_prediction(self.rdat1, self.rdat2):
            self.use_npc = True
            self.npc = pc + self.imm_b

        # self.use_npc = self.opcode in [Ops.JALR, Ops.JAL] or (self.opcode == Ops.BRANCH and not self.is_correct_prediction(self.rdat1, self.rdat2))

        if(self.opcode == Ops.BRANCH):
            if (self.is_correct_prediction(self.rdat1, self.rdat2) == False):
                self.npc = pc + self.imm_b
                self.use_npc = True
            # else:
                # self.npc = pc + 4
        elif (self.opcode == Ops.IMM):
            # self.wen = True                     ###
            pass
        elif(self.opcode == Ops.AUIPC):
            self.wdat = pc + self.imm_u
            # self.wen = True                     ###

        elif (self.opcode == Ops.JALR):
            self.npc = (self.imm_i + self.rdat1) & 0xFFFFFFFE
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
            # self.wen = True

        elif (self.opcode == Ops.STORE):
            self.ls_addr = self.rdat2 + self.imm_s
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
                if self.funct3 == Funct3.ECALL:
                    if self.regs[3] > 1:
                    # return False
                        raise Exception("Failure in test %x" % self.regs[3])
                    elif self.regs[3] == 1:
                        print("SUCCESS")
                    # tests passed successfully
                        # return False
                        raise Success("Success")

            # self.csr_addr = self.imm_i_unsigned
        else:
            pass
            # raise Exception("write op %x" % self.ins_hex)

    def is_correct_prediction(self, rdat1, rdat2):
        if (self.funct3 == Funct3.BEQ):
            return rdat1 == rdat2
        elif (self.funct3 == Funct3.BNE):
            return (rdat1 != rdat2)
        elif (self.funct3 == Funct3.BLT):
            return (rdat1 < rdat2)
        elif (self.funct3 == Funct3.BGE):
            return (rdat1 >= rdat2)
        elif (self.funct3 == Funct3.BLTU):
            return (unsigned(rdat1) < unsigned(rdat2))
        elif (self.funct3 == Funct3.BGEU):
            return unsigned(rdat1) >= unsigned(rdat2)

def ALU(aluop, a, b):
    if   aluop == Aluop.ADD:
        return a + b
    elif aluop == Aluop.SUB:  return a - b

    elif aluop == Aluop.SLL:  return a << (b & 0x1F)
    elif aluop == Aluop.SRL:  return a >> (b & 0x1F)
    elif aluop == Aluop.SRA:  return ((a & 0x7FFFFFFF) >> (b & 0x1F)) | (a & 0x80000000)

    elif aluop == Aluop.SLT:  return 1 if (a < b) else 0
    elif aluop == Aluop.SLTU: return 1 if (unsigned(a) < unsigned(b)) else 0

    elif aluop == Aluop.XOR:  return a ^ b
    elif aluop == Aluop.OR:   return a | b
    elif aluop == Aluop.AND:  return a & b

    else:
        raise Exception("alu op %s" % Funct3(aluop))

class ForwardingUnit:
    """
    Represent destination data as a list of dicts of rd : wdat.
    Hash the dicts to 
    """
    def __init__(self):
        self.data = []
        self.index = {}
        
    def insert(self, key, value):
        """
        key: rd
        value: wdat
        Append dict of key : val to the queue. 
        """
        self.data.append({'key' : key, 'value' : value})

    def build_index(self):
        """hash the queue of """
        index = {}
        for i in self.data:
            # TODO: watch for WAW
            index[i['key']] = i['value']
        return index

    def forward(self, rs1, rs2):
        """
        return rs1, rs2
        rs1 : forwarded value of rs1
        """
        index = self.build_index()
        print(index)
        rs1_fwd = index[rs1] if rs1 in index else None
        rs2_fwd = index[rs2] if rs2 in index else None
        return rs1_fwd, rs2_fwd

    def pop(self):
        """pop front of queue"""
        if len(self.data) > 0:
            self.data.pop()

    def __str__(self):
        as_string = ""
        self.build_index()
        print(self.data)
        return ""
        for k in self.index.keys():
            as_string = as_string + f"x{k}: {self.data[k]}  "
        return as_string
