import logging
import os
import unittest
from unittest.case import SkipTest

from parameterized import parameterized
from cpu_types import Fail, Success
from datapath import Datapath

# from stages import Decode, Execute, Fetch, ForwardingUnit, Memory, Ram, Writeback
# from support import Fail, ForwardingUnit, Ram, Success

# import mock

ADDR_BASE = 0x80000000


FORMAT = '%(message)s'
# print(f'{os.path}.log')
logging.basicConfig(filename=f'test_integration.log', format=FORMAT, filemode='w', level=logging.INFO)
logging.info("%s", f"{f'Stage':10}-- ({f'PC':8})")
logging.info("%s", "-" * 23)

def test_exit(wdat):
    if wdat != 1:
        raise Fail
    elif wdat == 1:
        raise Success


# class TestBranch(unittest.TestCase):
#     def setUp(self):
#         self.datapath = Datapath(test_exit)
        
#     def test_beq(self):
#         FILENAME = "asm/branch.o"
#         self.datapath.run(FILENAME)
        

# class TestStore(unittest.TestCase):
#     def setUp(self):
#         self.datapath = Datapath(test_exit)
        
#     def test_store(self):
#         FILENAME = "asm/store.o"
#         self.datapath.run(FILENAME)
#         self.assertEqual(4, self.datapath.ram[ADDR_BASE])

class TestForward(unittest.TestCase):
    def setUp(self):
        self.datapath = Datapath(test_exit)
        
    def test_de_ex(self):
        FILENAME = "asm/de_ex_forward.o"
        self.datapath.run(FILENAME)
        self.assertEqual(1, self.datapath.s2.regs[10])
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)
