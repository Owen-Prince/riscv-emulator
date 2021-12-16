import struct
from unittest.case import SkipTest
from parameterized import parameterized
import unittest

# from stages import Writeback, Memory, Execute, Decode, Fetch

from support import ForwardingUnit
# import mock


# class TestUtils(unittest.TestCase):

#     @parameterized.expand([
#         ["0",           0,          32,   0,],
#         ["negative 2",          -2,         32,   4294967294],
#         ["negative 3",          -3,         32,   4294967293],
#         ["negative 1",          -1,         32,   4294967295],
#         ["4294967295",  4294967295, 32,   4294967295],
#         ["0xFFFFFFFF",  0xFFFFFFFF, 32,   4294967295],
#         ["0x7FFFFFFF",  0x7FFFFFFF, 32,   4294967295 >> 1],
#         ["negative 2, 16b",     -2,         16,   65534],
#         ["negative 2, 8b",      -2,         8,    254],
#     ])
#     def test_unsigned(self, name, x, l, ans):
#         self.assertEqual(Utils.unsigned(x, l), ans)

#     @parameterized.expand([
#         ["ADDI",  0x00058513,      Aluop.ADD,],
#         ["SLLI",  0x00059513,      Aluop.SLL],
#         ["SLTI",  0x0005a513,      Aluop.SLT],
#         ["SLTIU", 0x0005b513,      Aluop.SLTU],
#         ["XORI",  0x0005c513,      Aluop.XOR],
#         ["SRLI",  0x0005d513,      Aluop.SRL],
#         ["SRAI",  0x4005d513,      Aluop.SRA],
#         ["ORI",   0x0005e513,      Aluop.OR],
#         ["ANDI",  0x0005f513,      Aluop.AND],
#         ["ADD",   0x00058533,      Aluop.ADD],
#         ["SUB",   0x40058533,      Aluop.SUB],
#         ["SLL",   0x00059533,      Aluop.SLL],
#         ["SLT",   0x0005a533,      Aluop.SLT],
#         ["SLTU",  0x0005b533,      Aluop.SLTU],
#         ["XOR",   0x0005c533,      Aluop.XOR],
#         ["SRL",   0x0005d533,      Aluop.SRL],
#         ["SRA",   0x4005d533,      Aluop.SRA],
#         ["OR",    0x0005e533,      Aluop.OR],
#         ["AND",   0x0005f533,      Aluop.AND],
#     ])
#     @unittest.skip("Broken")
#     def test_get_aluop_d(self, name, ins, aluop):
#         ins_d = Decode(ins, 0x0)
#         self.assertEqual(ins_d.aluop, aluop)

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





if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)