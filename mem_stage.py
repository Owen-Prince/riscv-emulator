import struct
import binascii
import logging
from PipelineStage import PipelineStage
from cpu_types import Ops, Utils


class Memory():
    """
    ws(addr, dat)
    r32(addr)
    """
    def __init__(self):
        self.memory = b'\x00'*0x4000
        
    # def r32(self, addr):
    #     addr -= 0x80000000
    #     if addr < 0 or addr >= len(self.memory):
    #         raise Exception("mem fetch to %x failed" % addr)
    #     assert addr >=0 and addr < len(self.memory)
    #     return struct.unpack("<I", self.memory[addr:addr+4])[0]
    def ws(self, addr, dat):
        addr -= 0x80000000
        assert addr >=0 and addr < len(self.memory)
        print(isinstance(dat, bytes))
        if isinstance(dat, bytes):
            dat = Utils.htoi(dat)
            print("true")
        self.memory = self.memory[:addr] + dat + self.memory[addr+len(dat):]

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

    def load(self, g):
        g.write(b'\n'.join([binascii.hexlify(self.memory[i:i+4][::-1]) for i in range(0,len(self.memory),4)]))
        
    def reset(self):
        self.memory =  b'\x00'*0x4000

class CSregs():
    def __init__(self):
        self.modified = {}
        self.cregs =  b'\x00'*0x4000
    def __getitem__(self, key):
        addr = key << 2
        return Utils.htoi(self.cregs[addr:addr+4])
    def __setitem__(self, key, val):
        addr = key << 2
        dat = struct.pack("<I", val & 0xFFFFFFFF) 
        self.cregs = self.cregs[:addr] + dat + self.cregs[addr+len(dat):]
        self.modified[key] = dat
        logging.debug("0x%s:  %s", key, Utils.zext(Utils.htoi(dat)))
    def __str__(self):
        s = ""
        for key, value in self.modified.items():
            s = s + f'0x{key:x}:  {Utils.zext(Utils.htoi(value)):s}\n'
        return s

    def print_modified(self):
        for key, value in self.modified.items():
            print(f'0x{key:x}:  {Utils.zext(Utils.htoi(value)):s}')

    def reset(self):
        self.csrs.cregs =  b'\x00'*0x4000



class Mem(PipelineStage):
    def __init__(self):
        super().__init__()

        self.memory = Memory()
        self.csrs = CSregs()
        self.wdat    = 0
        self.wen     = 0
        self.opcode  = 0
        self.ls_addr = 0
        self.rd      = 0
        self.rs1     = 0
        self.rs2     = 0

    def reset(self):
        self.memory.reset()
        self.csrs.reset()

    def update(self, ex):
        super().update(ex)
        self.wdat    = ex.wdat
        self.wen     = ex.wen
        self.opcode  = ex.opcode
        self.ls_addr = ex.ls_addr
        self.rd = ex.rd
        self.rs1 = ex.rs1
        self.rs2 = ex.rs2
        logging.info("MEMORY:    %s", self)

    def tick(self):
        if self.ins == -1: return
        if self.opcode == Ops.LOAD:
            self.wdat = self.memory[self.ls_addr]
        elif self.opcode == Ops.STORE:
            self.memory[self.ls_addr] = self.wdat

    