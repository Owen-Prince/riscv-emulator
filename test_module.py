import logging
import struct
import unittest
from unittest.case import SkipTest

from parameterized import parameterized

from stages import Decode, Execute, Fetch, Memory, Writeback
from stages import ForwardingUnit, Ram


# import mock

BASE_ADDR = 0x80000000
FORMAT = '%(message)s'

logging.basicConfig(filename='test.log', format=FORMAT, filemode='w', level=logging.INFO)
logging.info("%s", f"{f'Stage':10}-- ({f'PC':8})")
logging.info("%s", "-" * 23)
class TestForwarding(unittest.TestCase):
    """[(rd, wdat)], rs1, rs2"""
    @parameterized.expand([
        [[(1, 1), (1, 2)], 1, 2, (2, None)],
        [[(1, 1), (1, 2), (2, 3), (2, 4)], 1, 2, (2, 4)],
        [[(1, 1), (1, 2), (2, 3), (2, 4), (1, 3)], 1, 2, (3, 4)]
    ])
    def test_two(self, op_list, rs1, rs2, expected):
        fwd = ForwardingUnit()
        for l in op_list:
            rd, wdat = l
            fwd.insert(rd, wdat)
        # print(fwd)
        self.assertEqual(fwd.forward(rs1, rs2), expected)

class TestBranch(unittest.TestCase):
    def setUp(self):
        FILENAME = "assembly_unit_tests/branch.o"
        ram = Ram()
        self.s2 = Decode()
        self.s1 = Fetch(ram)
        ram.load(FILENAME)

    def step(self):
        self.s2.tick(self.s1)
        self.s1.tick(decode=self.s2)
        logging.info("-"*20)
        
    def test_beq(self):
        for i in range(7): 
            self.step()

class TestRam(unittest.TestCase):
    def test_ram (self):
        ram = Ram()
        ram[0x80000000] = struct.pack("I", 1234)
        print(ram.memory[0:4])
        assert(struct.pack("I", 1234) == ram.memory[0:4])
    def test_load(self):
        FILENAME = "asm/branch.o"
        ram = Ram()
        ram.load(FILENAME)
        print(ram.memory[0:100])

class TestForwarding(unittest.TestCase):
    def setUp(self) -> None:
        self.ram = Ram()
        self.s4  = Memory()
        self.s3  = Execute()
        self.s2  = Decode()
        self.s1  = Fetch(self.ram)


    def tick(self):
        fwd = ForwardingUnit()
        
        # Memory <- Execute
        r = self.s4.tick(self.s3, ram=self.ram)
        fwd.insert(rd=self.s4.ins.rd, wdat=self.s4.ins.wdat)
        
        # Execute <- Decode
        self.s3.tick(self.s2)
        fwd.insert(rd=self.s3.ins.rd, wdat=self.s3.ins.wdat)
        
        # Decode <- Fetch
        self.s2.tick(self.s1)

        # Fetch
        self.s1.tick(decode=self.s2)

    def test_de_ex_fwd(self):
        self.ram.load(filename="asm/forward.o")


        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)
