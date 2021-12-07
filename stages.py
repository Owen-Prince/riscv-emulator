import logging
import struct
import binascii
from cpu_types import Ops, gib

from support import ALU, Instruction, Regfile, pad

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
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins}"
        # if self.name == "Fetch":
        # logging.info("%s", self.format())
        
    def tick(self, prev):
        self.pc = prev.pc
        self.ins_hex = prev.ins_hex
        self.ins = prev.ins
        self.update()
        logging.info("%s", self.format())
        return self.ins

    def update(self):
        pass

class Fetch(Stage):
    """
    tick(prev)
    fetch(pc)
    """
    def __init__(self, ram, pc=0x80000000):
        super().__init__("Fetch", pc)
        self.npc = self.pc
        self.use_npc = False
        self.ram = ram
        self.ins_hex = self.fetch(self.pc)
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}\t\t\t\tnpc = {self.npc}, take_npc = {self.use_npc}"
        
    def tick(self, decode=None):
        self.ins_hex = self.fetch(self.pc)
        super().tick(self)
        self.use_npc = decode.ins.use_npc
        self.npc = decode.ins.npc if decode and decode.ins.use_npc else self.pc + 4
        # print(self.pc - 0x80000000, self.npc - 0x80000000, f"{self.ins_hex:x}")
        self.pc = self.npc
        
    def fetch(self, pc):
        return self.ram[pc]

    def update(self):
        # print("fetch")
        # opcode = Ops(gib(self.ins_hex, 6, 0))
        pass

        
class Decode(Stage):
    def __init__(self):
        super().__init__("Decode")
        self.regs = Regfile()
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins}\t rs1 = {self.ins.rs1}, rs2 = {self.ins.rs2}, rd = {self.ins.rd} | npc = {self.ins.npc}, use_npc = {self.ins.use_npc}"


    def wb(self, prev):
        self.regs[prev.ins.rd] = prev.ins.wdat if prev.ins.wen else self.regs[prev.ins.rd]
        
    def tick(self, prev):
        super().tick(prev)

    def update(self):
        if self.flush: self.ins_hex = 0x0 
        self.ins = Instruction(self.ins_hex, regs=self.regs)
        self.ins.set_control_signals(self.pc)
        self.flush = self.ins.use_npc
        # print("decode")
        
        # self.ins = 

class Execute(Stage):
    def __init__(self):
        super().__init__("Execute")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins} -- wen = {self.ins.wen:5}, wdat = {self.ins.wdat:8x}, wsel = {self.ins.rd}"

    def update(self):
        if self.ins.opcode == Ops.OP:
            self.ins.wdat = ALU(self.ins.aluop, self.ins.rdat1, self.ins.rdat2)
        if self.ins.opcode == Ops.IMM:
            self.ins.wdat = ALU(self.ins.aluop, self.ins.rdat1, self.ins.imm_i)

class Memory(Stage):
    def __init__(self):
        super().__init__("Memory")
        

class Writeback(Stage):
    def __init__(self):
        super().__init__("Writeback")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins} -- wen = {self.ins.wen:5}, wdat = {self.ins.wdat:8x}, wsel = {self.ins.rd}"
