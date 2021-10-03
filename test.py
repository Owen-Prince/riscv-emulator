import struct
from decode_stage import Decode
from cpu_types import Ops, Funct3
import unittest

class TestDecodeMethods(unittest.TestCase):
    def setUp(self):
        self.d = Decode(0x0)

    def test_BEQ(self):
        self.d.funct3 = Funct3.BEQ
        self.assertEqual(self.d.resolve_branch(-3,-2), False)
        self.assertEqual(self.d.resolve_branch(1,1), True)
    def test_BNE(self):
        self.d.funct3 = Funct3.BNE
        self.assertEqual(self.d.resolve_branch(-3,-2), True)
        self.assertEqual(self.d.resolve_branch(1,1), False)
    def test_BLT(self):
        self.d.funct3 = Funct3.BLT
        self.assertEqual(self.d.resolve_branch(-3,-2), True)
        self.assertEqual(self.d.resolve_branch(-2,-3), False)
        self.assertEqual(self.d.resolve_branch(2,3),   True)
        self.assertEqual(self.d.resolve_branch(3,2),   False)
        self.assertEqual(self.d.resolve_branch(3,3),   False)
    def test_BGE(self):
        self.d.funct3 = Funct3.BGE
        self.assertEqual(self.d.resolve_branch(-3,-2), False)
        self.assertEqual(self.d.resolve_branch(-2,-3), True)
        self.assertEqual(self.d.resolve_branch(2,3),   False)
        self.assertEqual(self.d.resolve_branch(3,2),   True)
        self.assertEqual(self.d.resolve_branch(3,3),   True)
    def test_BLTU(self):
        self.d.funct3 = Funct3.BLTU
        self.assertEqual(self.d.resolve_branch(-3,-2), False)
        self.assertEqual(self.d.resolve_branch(-2,-3), True)
        self.assertEqual(self.d.resolve_branch(2,3),   True)
        self.assertEqual(self.d.resolve_branch(3,2),   False)
        self.assertEqual(self.d.resolve_branch(3,3),   False)
    def test_BGEU(self):
        self.d.funct3 = Funct3.BGEU
        self.assertEqual(self.d.resolve_branch(-3,-2), True)
        self.assertEqual(self.d.resolve_branch(-2,-3), False)
        self.assertEqual(self.d.resolve_branch(2,3),   False)
        self.assertEqual(self.d.resolve_branch(3,2),   True)
        self.assertEqual(self.d.resolve_branch(3,3),   True)

if __name__ == '__main__':
    unittest.main(verbosity=2)