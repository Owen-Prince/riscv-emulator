import struct
from decode_stage import Decode
from cpu_types import Ops, Funct3, Utils, Aluop
import unittest
from parameterized import parameterized
from execute_stage import Execute


class TestUtils(unittest.TestCase):

    @parameterized.expand([
        ["0",           0,          32,   0,],
        ["negative 2",          -2,         32,   4294967294],
        ["negative 3",          -3,         32,   4294967293],
        ["negative 1",          -1,         32,   4294967295],
        ["4294967295",  4294967295, 32,   4294967295],
        ["0xFFFFFFFF",  0xFFFFFFFF, 32,   4294967295],
        ["0x7FFFFFFF",  0x7FFFFFFF, 32,   4294967295 >> 1],
        ["negative 2, 16b",     -2,         16,   65534],
        ["negative 2, 8b",      -2,         8,    254],
    ])
    def test_unsigned(self, name, x, l, ans):
        self.assertEqual(Utils.unsigned(x, l), ans)


    @parameterized.expand([
        ["ADDI",  0x00058513,      Aluop.ADD,],
        ["SLLI",  0x00059513,      Aluop.SLL],
        ["SLTI",  0x0005a513,      Aluop.SLT],
        ["SLTIU", 0x0005b513,      Aluop.SLTU],
        ["XORI",  0x0005c513,      Aluop.XOR],
        ["SRLI",  0x0005d513,      Aluop.SRL],
        ["SRAI",  0x4005d513,      Aluop.SRA],
        ["ORI",   0x0005e513,      Aluop.OR],
        ["ANDI",  0x0005f513,      Aluop.AND],
        ["ADD",   0x00058533,      Aluop.ADD],
        ["SUB",   0x40058533,      Aluop.SUB],
        ["SLL",   0x00059533,      Aluop.SLL],
        ["SLT",   0x0005a533,      Aluop.SLT],
        ["SLTU",  0x0005b533,      Aluop.SLTU],
        ["XOR",   0x0005c533,      Aluop.XOR],
        ["SRL",   0x0005d533,      Aluop.SRL],
        ["SRA",   0x4005d533,      Aluop.SRA],
        ["OR",    0x0005e533,      Aluop.OR],
        ["AND",   0x0005f533,      Aluop.AND],
    ])
    def test_get_aluop_d(self, name, ins, aluop):
        ins_d = Decode(ins)
        self.assertEqual(ins_d.aluop_d, aluop)



class TestExecute(unittest.TestCase):

    @parameterized.expand([
        ["ADDI",  Aluop.ADD,    0xa, 0xb, 0x15],
        ["SUB",   Aluop.SUB,    0xa, 0xb, -1],
        ["SLLI",  Aluop.SLL,    0x1, 0x3, 0x8],
        ["SLTI",  Aluop.SLT,    -5,    5, 1],
        ["SLTIU", Aluop.SLTU,   -5,    5, 0],
        ["SLTIU", Aluop.SLTU,    4,    5, 1],
        ["SLTIU", Aluop.SLTU,    4,   -5, 1],
        ["XOR",   Aluop.XOR,    0xaa, 0x55, 0xff],
        ["SRL",   Aluop.SRL,    0x80000008, 0x3, 0x10000001],
        ["SRA",   Aluop.SRA,    0x80000008, 0x3, 0x80000001],
        ["OR",    Aluop.OR,     0xaa, 0x55, 0xff],
        ["AND",   Aluop.AND,    0xaa, 0xcc, 0x88],
    ])
    def test_ALU(self, name, aluop, a, b, expected):
        self.assertEqual(Execute.ALU(aluop, a, b), expected)




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
        self.assertEqual(self.d.resolve_branch(-3,-2), True)
        self.assertEqual(self.d.resolve_branch(-2,-3), False)
        self.assertEqual(self.d.resolve_branch(2,3),   True)
        self.assertEqual(self.d.resolve_branch(3,2),   False)
        self.assertEqual(self.d.resolve_branch(3,3),   False)
    def test_BGEU(self):
        self.d.funct3 = Funct3.BGEU
        self.assertEqual(self.d.resolve_branch(-3,-2), False)
        self.assertEqual(self.d.resolve_branch(-2,-3), True)
        self.assertEqual(self.d.resolve_branch(2,3),   False)
        self.assertEqual(self.d.resolve_branch(3,2),   True)
        self.assertEqual(self.d.resolve_branch(3,3),   True)

# class TestExecuteMethods(unittest.TestCase):


if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)