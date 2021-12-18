import logging
import unittest
from unittest.case import SkipTest

from parameterized import parameterized

from stages import Decode, Execute, Fetch, Memory, Writeback
from support import Fail, ForwardingUnit, Ram, Success

# import mock


FORMAT = '%(message)s'

logging.basicConfig(filename='test_integration.log', format=FORMAT, filemode='w', level=logging.INFO)
logging.info("%s", f"{f'Stage':10}-- ({f'PC':8})")
logging.info("%s", "-" * 23)

class Pipeline(unittest.TestCase):
    def setUp(self):
        self.ram = Ram()
        self.s5  = Writeback()
        self.s4  = Memory()
        self.s3  = Execute()
        self.s2  = Decode()
        self.s1  = Fetch(self.ram)

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
            self.s4.tick(self.s3)
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

class TestBranch(Pipeline):
    def setUp(self):
        super().setUp()
        FILENAME = "asm/branch.o"
        
        self.ram.load(FILENAME)
        
    def test_beq(self):
        while self.step():
            pass
        print(self.s2.regs)
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)
