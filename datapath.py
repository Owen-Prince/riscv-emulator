# from support import Fail, ForwardingUnit, Ram, Success
import logging
import struct
import copy
from types import FunctionType

from cpu_types import Fail, Success
from ForwardingUnit import ForwardingUnit
from HazardUnit import HazardUnit
from Ram import Ram
from stages import Decode, Execute, Fetch, Memory, Writeback


class Datapath():
    def __init__(self, exit_func, base_addr: int):
        self.ram = Ram(base_addr=base_addr)
        self.s5  = Writeback(exit_func)
        self.s4  = Memory()
        self.s3  = Execute()
        self.s2  = Decode()
        self.s1  = Fetch(self.ram, pc=base_addr)

        self.inscnt = 0

    def run(self, filename: str):
        self.ram.load(filename)
        self.s1.ins_hex = self.s1.fetch(self.s1.pc)
        logging.info("%s", f"CLK CYCLE : {self.inscnt} {f'-'*24}")
        # print(f"{self.s1.pc:x}")
        while(self.step()):
            self.inscnt += 1
            # print(f'{self.s1.pc:x} {self.s2.pc:x}')

            logging.info("%s", f"CLK CYCLE : {self.inscnt} {f'-'*24}")
        print(self.s2.regs)
        # print(self.memory.regs)

    def eval(self):
        """
        use same name as verilator here
        update the state of the processor
        """
        try:
            fwd = ForwardingUnit()
            hzd = HazardUnit(f=self.s1, d=self.s2, e=self.s3, m=self.s4, w=self.s5)
            
            # Decode <- Writeback
            self.s2.wb(prev=self.s5)
            
            # Writeback <- Memory
            self.s5.tick(prev=self.s4, fwd=None)
            fwd.insert(ins=self.s5.ins)
            
            # Memory <- Execute
            r = self.s4.tick(prev=self.s3, ram=self.ram, fwd=fwd)
            self.ram = copy.copy(r)
            fwd.insert(ins=self.s4.ins)
            
            # Execute <- Decode
            self.s3.tick(prev=self.s2, fwd=fwd)
            fwd.insert(ins=self.s3.ins)
            
            # Decode <- Fetch
            self.s2.tick(prev=self.s1, fwd=fwd)

            # Fetch
            self.s1.tick(decode=self.s2)
            
            logging.info("Forwarding Unit " + "-"*59)
            logging.info("%s", fwd)
            logging.info("-"*75)

        except:
            raise

    def step(self):
        """wrapper for eval that contains exception logic"""
        try:
            self.eval()
        except (Success, Fail) as e:
            return False
        except Exception as e:
            print("Error", repr(e))
            raise
        return True
