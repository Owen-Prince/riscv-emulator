import binascii
import logging
import struct

from elftools.elf.elffile import ELFFile
from cpu_types import Ops, gib, pad, sign_extend, unsigned, Funct3, Aluop, Success, Fail

# from support import Regfile
from Instruction import Instruction



class Stage:
    """
    tick(prev)
    """
    def __init__(self, name, pc=0x0):
        self.pc = pc
        self.ins_hex = 0
        self.name = name
        self.ins = Instruction(0)
        self.flush = False
        self.stall = False
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins}"

        # if self.name == "Fetch":
        # logging.info("%s", self.format())
        
    def tick(self, prev):
        """
        prev: the previous stage
        all the update logic happens here. calls the update()
        function, which should be overridden by child 
        classes. 
        """
        if not self.stall:
            self.pc = prev.pc
            self.ins_hex = prev.ins_hex
            self.ins = prev.ins
            logging.info("%s", self.format())
            
            self.update()
        # return {'rd' : self.ins.rd, 'wdat' : self.ins.wdat}
        # return self.ins

    def update(self):
        """template function to be overridden"""
        pass

    def flush_logic(self):
        """checks """
        if self.flush:
            self.ins_hex = 0x0
            self.ins = Instruction(0x0)



class Fetch(Stage):
    """
    Fetch stage
    tick(prev)
    fetch(pc)
    """
    def __init__(self, ram, pc=0x80000000):
        super().__init__("Fetch", pc)
        self.npc = self.pc
        self.use_npc = False
        self.ram = ram
        self.ins_hex = self.fetch(self.pc)
        self.ins = Instruction(self.ins_hex)
        # print(f"\nFetch: {self.pc:x}, {self.ins}")


        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}{f' ':31}| npc = {pad(hex(self.npc)[2:])}, use_npc = {self.use_npc}"
    
        
    def tick(self, decode=None):
        """
        fetch instruction from instruction memory
        if branch or jump, use the branch/jump pc otherwise use pc + 4
        """
        if not self.stall:
            self.use_npc = decode.ins.use_npc
            self.npc = decode.ins.npc if decode and decode.ins.use_npc else self.pc + 4
            self.pc = self.npc
            self.ins_hex = self.fetch(self.pc)
            self.ins = Instruction(self.ins_hex)

            super().tick(self)
            # print(f"Fetch: {self.pc:x}, {self.ins}")

        
    def fetch(self, pc):
        return self.ram[pc]

    def update(self):
        opcode = Ops(gib(self.ins_hex, 6, 0))
        pass

class Decode(Stage):
    """
    Decode stage
    Write results to regs before update
    """
    def __init__(self):
        super().__init__("Decode")
        self.regs = Regfile()
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins} | npc = {self.ins.npc:8}, use_npc = {self.ins.use_npc}"


    def wb(self, prev):
        """update registers with values from writeback stage"""
        self.regs[prev.ins.rd] = prev.ins.wdat if prev.ins.wen else self.regs[prev.ins.rd]
        
    def tick(self, prev):
        super().tick(prev)

    def update(self):
        """
        Set control signals based on hex value of instruction
        """
        self.flush_logic()
        self.ins = Instruction(self.ins_hex, regs=self.regs)
        self.ins.set_control_signals(pc=self.pc)
        self.flush = self.ins.use_npc
        # self.ins = 

class Execute(Stage):
    """
    Execute stage
    """
    def __init__(self):
        super().__init__("Execute")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {str(self.ins):24} | wen = {self.ins.wen:<}, wdat = {pad(hex(self.ins.wdat)[2:]):8}, wsel = {self.ins.rd}"

    def update(self):
        if self.ins.opcode == Ops.OP:
            self.ins.wdat = ALU(self.ins.aluop, self.ins.rdat1, self.ins.rdat2)
        if self.ins.opcode == Ops.IMM:
            self.ins.wdat = ALU(self.ins.aluop, self.ins.rdat1, self.ins.imm_i)

class Memory(Stage):
    """
    Memory stage
    """

    def __init__(self):
        super().__init__("Memory")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {str(self.ins):24} | wen = {self.ins.wen:<}, wdat = {pad(hex(self.ins.wdat)[2:]):8}, wsel = {self.ins.rd}"
        
    def tick(self, prev, ram):
        super().tick(prev)
        if self.ins.opcode is Ops.LOAD:
            self.ins.wdat = ram[self.ins.ls_addr]
            if (self.ins.funct3 == Funct3.LW):
                self.ins.wdat = ram[self.ins.ls_addr]
            elif (self.ins.funct3 == Funct3.LH):
                self.ins.wdat = sign_extend(ram[self.ins.ls_addr] & 0xFFFF)
            elif (self.ins.funct3 == Funct3.LB):
                self.ins.wdat = sign_extend(ram[self.ins.ls_addr] & 0xFF)
            elif (self.ins.funct3 == Funct3.LHU):
                self.ins.wdat = ram[self.ins.ls_addr] & 0xFFFF
            elif (self.ins.funct3 == Funct3.LBU):
                self.ins.wdat = ram[self.ins.ls_addr] & 0xFF

                
        if self.ins.opcode is Ops.STORE:
            ram[self.ins.ls_addr] = struct.pack("I", self.ins.wdat)
    def update(self):
        pass
        

class Writeback(Stage):
    """
    Writeback stage
    """
    def __init__(self):
        super().__init__("Writeback")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {str(self.ins):24} | wen = {self.ins.wen:<}, wdat = {pad(hex(self.ins.wdat)[2:]):8}, wsel = {self.ins.rd}"

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
        # print(struct.pack("I", val))
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

class ForwardingUnit:
    """
    Represent destination data as a list of dicts 
    of rd : wdat.
    build_index does a hash of the list of dicts 
    """
    def __init__(self):
        self.data = []
        self.index = {}
        
    def insert(self, rd, wdat):
        """
        Append dict of rd : val to the queue. 
        """
        self.data.append({'rd' : rd, 'wdat' : wdat})

    def build_index(self):
        """hash the list of """
        index = {}
        for i in self.data:
            # TODO: watch for WAW
            index[i['rd']] = i['wdat']
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

class HazardUnit():
    def __init__(self, f: Fetch, d: Decode, e: Execute, m: Memory, w: Writeback):

        self.f = f
        self.d = d
        self.e = e
        self.m = m

        self.stall_f = self.f.busy
        self.stall_d = self.d.busy
        self.stall_e = self.e.busy
        self.stall_m = self.m.busy

        self.load_use()
        self.stall_prev_stages()


    def load_use(self) -> None:
        """
        Load in mem stage:
            ex-mem
            de-mem
        Load in Ex stage:
            de-ex
        """
        if self.m.ins.opcode == Ops.Load:
            rd = self.m.ins.rd
            if self.e.ins.rs1 == rd or self.e.ins.rs2 == rd:
                self.stall_e = True
            if self.d.ins.rs1 == rd or self.d.ins.rs2 == rd:
                self.stall_d = True
        if self.e.ins.opcode == Ops.Load:
            rd = self.e.ins.rd
            if self.d.ins.rs1 == rd or self.d.ins.rs2 == rd:
                self.stall_d = True

    def stall_prev_stages(self) -> None:
        """
        Stall all previous stages
        """
        if self.stall_m:
            self.stall_e = True
        if self.stall_e:
            self.stall_d = True
        if self.stall_d:
            self.stall_f = True