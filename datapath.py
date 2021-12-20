# from support import Fail, ForwardingUnit, Ram, Success
import logging
import struct

from cpu_types import Fail, Success
from ForwardingUnit import ForwardingUnit
from HazardUnit import HazardUnit
from Ram import Ram
from stages import Decode, Execute, Fetch, Memory, Writeback


class Datapath():
    def __init__(self, exit_func):
        self.ram = Ram()
        self.s5  = Writeback(exit_func)
        self.s4  = Memory()
        self.s3  = Execute()
        self.s2  = Decode()
        self.s1  = Fetch(self.ram)

        self.inscnt = 0

    def run(self, filename):
        self.ram.load(filename)
        self.s1.ins_hex = self.s1.fetch(self.s1.pc)
        logging.info("%s", f"CLK CYCLE : {self.inscnt} {f'-'*24}")
        # print(f"{self.s1.pc:x}")
        while(self.step()):
            self.inscnt += 1
            # print(f'{self.s1.pc:x} {self.s2.pc:x}')

            logging.info("%s", f"CLK CYCLE : {self.inscnt} {f'-'*24}")
        print(self.s2.regs)

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
            fwd.insert(ins=self.s4.ins)

            # print(r[0x80000000])
            # for i in range(16):
                # print(f"{i*4 + 0x80000000:x}")
                # self.ram[0x80000000 + i*4] = struct.pack("I", r[0x80000000 + i*4])

            # fwd.insert(rd=self.s4.ins.rd, wdat=self.s4.ins.wdat)
            
            # Execute <- Decode
            self.s3.tick(prev=self.s2, fwd=fwd)
            fwd.insert(ins=self.s3.ins)
            # print(fwd.data)
            # fwd.insert(rd=self.s3.ins.rd, wdat=self.s3.ins.wdat)
            
            # Decode <- Fetch
            # print(fwd.forward(rs1=self.s2.ins.rs1, rs2=self.s2.ins.rs2))
            self.s2.tick(prev=self.s1, fwd=fwd)

            # Fetch
            self.s1.tick(decode=self.s2)
            
            logging.info("Forwarding Unit " + "-"*59)
            logging.info("%s", fwd)
            logging.info("-"*75)

            # logging.info("-"*74)
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
