import binascii
import logging
import struct

from elftools.elf.elffile import ELFFile
from ForwardingUnit import ForwardingUnit
from Ram import Ram
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
        self.busy = False
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins}"

        # if self.name == "Fetch":
        # logging.info("%s", self.format())
        
    def tick(self, prev, fwd: ForwardingUnit=None):
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
            if fwd:
                self.ins = fwd.forward(self.ins)
                
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
        self.prev_pc = self.pc


        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}{f' ':31}| npc = {pad(hex(self.npc)[2:])}, use_npc = {self.use_npc}"
    
        
    def tick(self, decode=None):
        """
        fetch instruction from instruction memory
        if branch or jump, use the branch/jump pc otherwise use pc + 4
        """
        if not self.stall:
            self.use_npc = decode.ins.use_npc
            self.npc = decode.ins.npc if decode and decode.ins.use_npc else self.pc + 4
            self.prev_pc = self.pc	
            self.pc = self.npc
            self.ins_hex = self.fetch(self.pc)
            self.ins = Instruction(self.ins_hex)
            logging.info("%s", self.format())


        
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
        self.prev_pc = self.pc
        self.regs = Regfile()
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins} | npc = {self.ins.npc:8}, use_npc = {self.ins.use_npc}, prev_pc = {self.prev_pc:x}"


    def wb(self, prev: Stage):
        """update registers with values from writeback stage"""
        self.regs[prev.ins.rd] = prev.ins.wdat if prev.ins.wen else self.regs[prev.ins.rd]
        
    def tick(self, prev: Stage, fwd: ForwardingUnit):
        self.prev_pc = prev.prev_pc
        super().tick(prev, fwd=fwd)


    def update(self):
        """
        Set control signals based on hex value of instruction
        """
        self.flush_logic()
        self.ins = Instruction(self.ins_hex, regs=self.regs)
        self.ins.set_control_signals(pc=self.pc)

class Execute(Stage):
    """
    Execute stage
    """
    def __init__(self):
        super().__init__("Execute")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {str(self.ins):24} | wen = {self.ins.wen:<}, wdat = {pad(hex(self.ins.wdat)[2:]):8}, wsel = {self.ins.rd}"

    def update(self):
        if self.ins.opcode == Ops.OP:
            self.ins.wdat = ALU(self.ins.aluop, self.ins.rdat1, self.rdat2)
        if self.ins.opcode == Ops.IMM:
            self.ins.wdat = ALU(self.ins.aluop, self.ins.rdat1, self.ins.imm_i)

class Memory(Stage):
    """
    Memory stage
    """

    def __init__(self):
        super().__init__("Memory")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {str(self.ins):24} | wen = {self.ins.wen:<}, wdat = {pad(hex(self.ins.wdat)[2:]):8}, wsel = {self.ins.rd}"
        
    def tick(self, prev: Stage, ram: Ram, fwd: ForwardingUnit):
        super().tick(prev, fwd=fwd)
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
            print(f"{self.ins.ls_addr:x}")
            ram[self.ins.ls_addr] = struct.pack("I", self.ins.wdat)
        return ram 
    def update(self):
        pass
        

class Writeback(Stage):
    """
    Writeback stage
    """
    def __init__(self, exit_func):
        self.exit_func = exit_func
        super().__init__("Writeback")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {str(self.ins):24} | wen = {self.ins.wen:<}, wdat = {pad(hex(self.ins.wdat)[2:]):8}, wsel = {self.ins.rd}"
    def update(self):
        if self.ins.opcode is Ops.SYSTEM and self.ins.funct3 is Funct3.ECALL:
            self.exit_func(self.ins.wdat)


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



