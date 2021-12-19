# from support import Fail, ForwardingUnit, Ram, Success
from cpu_types import Fail, Success
from stages import Fetch, Decode, Execute, ForwardingUnit, Memory, Ram, Writeback
import logging


class Datapath():
    def __init__(self):
        self.ram = Ram()
        self.s5  = Writeback()
        self.s4  = Memory()
        self.s3  = Execute()
        self.s2  = Decode()
        self.s1  = Fetch(self.ram)

        self.inscnt = 0

    def run(self, filename):
        self.ram.load(filename)
        self.s1.ins_hex = self.s1.fetch(self.s1.pc)
        logging.info("%s", f"CLK CYCLE : {self.inscnt} {f'-'*24}")
        print(f"{self.s1.pc:x}")
        while(self.step()):
            self.inscnt += 1
            print(f'{self.s1.pc:x} {self.s2.pc:x}')

            logging.info("%s", f"CLK CYCLE : {self.inscnt} {f'-'*24}")
        print(self.s2.regs)

    def eval(self):
        """
        use same name as verilator here
        update the state of the processor
        """
        try:
            fwd = ForwardingUnit()
            
            # Decode <- Writeback
            self.s2.wb(prev=self.s5)
            
            # Writeback <- Memory
            self.s5.tick(self.s4)
            fwd.insert(rd=self.s5.ins.rd, wdat=self.s5.ins.wdat)
            
            # Memory <- Execute
            self.s4.tick(self.s3, ram=self.ram)
            fwd.insert(rd=self.s4.ins.rd, wdat=self.s4.ins.wdat)
            
            # Execute <- Decode
            self.s3.tick(self.s2)
            fwd.insert(rd=self.s3.ins.rd, wdat=self.s3.ins.wdat)
            
            # Decode <- Fetch
            self.s2.tick(self.s1)

            # Fetch
            self.s1.tick(decode=self.s2)
            
            logging.info("-"*20)
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