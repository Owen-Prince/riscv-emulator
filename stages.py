import logging
from cpu_types import Ops

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
        """
        prev: the previous stage
        all the update logic happens here. calls the update()
        function, which should be overridden by the child 
        classes. 
        """
        self.pc = prev.pc
        self.ins_hex = prev.ins_hex
        self.ins = prev.ins
        self.update()
        logging.info("%s", self.format())
        return {'rd' : self.ins.rd, 'wdat' : self.ins.wdat}
        # return self.ins

    def update(self):
        """template function to be overridden"""
        pass

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
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}\t\t\t\tnpc = {pad(hex(self.npc)[2:])}, take_npc = {self.use_npc}"
        
    def tick(self, decode=None):
        """
        fetch instruction from instruction memory
        if branch or jump, use the branch/jump pc otherwise use pc + 4
        """
        self.ins_hex = self.fetch(self.pc)
        super().tick(self)
        self.use_npc = decode.ins.use_npc
        self.npc = decode.ins.npc - 4 if decode and decode.ins.use_npc else self.pc + 4
        self.pc = self.npc
        
    def fetch(self, pc):
        return self.ram[pc]

    def update(self):
        # print("fetch")
        # opcode = Ops(gib(self.ins_hex, 6, 0))
        pass

class Decode(Stage):
    """
    Decode stage
    Write results to regs before update
    """
    def __init__(self):
        super().__init__("Decode")
        self.regs = Regfile()
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins}\t rs1 = {self.ins.rs1}, rs2 = {self.ins.rs2}, rd = {self.ins.rd} | npc = {self.ins.npc}, use_npc = {self.ins.use_npc}"


    def wb(self, prev):
        """update registers with values from writeback stage"""
        self.regs[prev.ins.rd] = prev.ins.wdat if prev.ins.wen else self.regs[prev.ins.rd]
        
    def tick(self, prev):
        super().tick(prev)

    def update(self):
        if self.flush: 
            self.ins_hex = 0x0
        self.ins = Instruction(self.ins_hex, regs=self.regs)
        self.ins.set_control_signals(self.pc)
        self.flush = self.ins.use_npc
        # self.ins = 

class Execute(Stage):
    """
    Execute stage
    """
    def __init__(self):
        super().__init__("Execute")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins} -- wen = {self.ins.wen:5}, wdat = {self.ins.wdat:8x}, wsel = {self.ins.rd}"

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

class Writeback(Stage):
    """
    Writeback stage
    """
    def __init__(self):
        super().__init__("Writeback")
        self.format = lambda : f"{self.name:10s}-- ({self.pc:8x}): ins_hex = {pad(hex(self.ins_hex)[2:])}, {self.ins} -- wen = {self.ins.wen:5}, wdat = {self.ins.wdat:8x}, wsel = {self.ins.rd}"
