import logging
import unittest
from unittest.case import SkipTest

from parameterized import parameterized

from stages import Decode, Fetch
from support import ForwardingUnit, Ram

# import mock


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

        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)
