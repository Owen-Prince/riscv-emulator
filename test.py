import struct
from unittest.case import SkipTest

from elftools.construct import Byte
from elftools.elf.elffile import ELFFile
from unittest.mock import Mock
from decode_stage import Decode
from cpu_types import Ops, Funct3, Utils, Aluop
import unittest
import binascii
from parameterized import parameterized
from execute_stage import Execute
from fetch_stage import InsFetch
from mem_stage import Memory
# import mock

def init_mem(filename):
    mem = Memory()
    with open("riscv-tests/isa/" + filename, 'rb') as f:
        e = ELFFile(f)
        for s in e.iter_segments():
            mem[s.header.p_paddr] =  s.data()
        # with open("test-cache/%s" % filename.split("/")[-1], "wb") as g:
            # g.write(b'\n'.join([binascii.hexlify(mem[i:i+4][::-1]) for i in range(0,len(mem),4)]))
    return mem

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
    @unittest.skip("Broken")
    def test_get_aluop_d(self, name, ins, aluop):
        ins_d = Decode(ins, 0x0)
        self.assertEqual(ins_d.aluop, aluop)

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

# class TestFetch(unittest.TestCase):
#     @parameterized.expand([
#         ["AUIPC",  Ops.AUIPC, Funct3.ADD, 0xa, 0xb, 0x15],
#     ])
#     testOp(self, name, aluop):

class TestDecodeMethods(unittest.TestCase):
    def setUp(self):
        self.d = Decode(0x0, 0x0)

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

class TestFetch(unittest.TestCase):
    def setUp(self):
        self.mem = init_mem("rv32ui-p-add")
        self.ifetch = InsFetch(self.mem)

    # tobytes = lambda x : bytes([int(x[i:i+8], 2) for i in range(0, len(x), 8)])
    # def testUpdate(self):
    #     self.ifetch.update(self.mem, 0x80000000, False)
    #     self.ifetch.tick()
    #     self.assertEqual(self.ifetch.pc, 0x80000004)

    # def testBranch(self):
    #     self.ifetch.update(self.mem, 0x8000000A, True)
    #     self.ifetch.tick()
    #     self.assertEqual(self.ifetch.pc, 0x8000000A)

class TestDecode(unittest.TestCase):
    def setUp(self):
        # self.mem = init_mem("rv32ui-p-add")
        self.decode = Decode()
        self.ifs = Mock()
        self.wb = Mock()
        
        
        

    def testWrite(self):
        self.wb.wen = 1
        self.wb.wdat = 0xabcd
        self.wb.rd = 1
        self.ifs.ins = 0x00000113
        # print(self.ifs.ins)
        self.ifs.pc = 0x80000000
        self.decode.update(self.ifs, self.wb)
        self.decode.tick()
        self.assertEqual(self.wb.wdat, self.decode.regfile[1])
        # print(self.decode.regfile)

# def init_mem(self):
#     for x in glob.glob("riscv-tests/isa/"+"rv32ui-p-*"):
#     if x.endswith('.dump'):
#         continue
#     with open(x, 'rb') as f:
#         mem.reset()
#         de.reset()
#         logging.info("test %s\n", x)
#         e = ELFFile(f)
#         for s in e.iter_segments():
#             mem[s.header.p_paddr] = s.data()
#         with open("test-cache/%s" % x.split("/")[-1], "wb") as g:
#             mem.load(g)
#         ins_f.pc = (0x80000000) 

#         inscnt = 0
#         while step():
#             inscnt += 1



if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)