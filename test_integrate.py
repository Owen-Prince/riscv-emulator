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
from mem_stage import Mem, Memory
from wb_stage import Wb
import logging
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


class TestIfDe(unittest.TestCase):
    def setUp(self):
        self.mem = init_mem("rv32ui-p-add")
        self.ifs = InsFetch(self.mem)
        self.de = Decode()
        self.wb = Mock()
        self.wb.wen = 0
        self.wb.wdat = 0xabcd
        self.wb.rd = 1

    
    def testUpdate(self):

        for i in range(10):
            self.ifs.tick()
            self.de.update(self.ifs, self.wb)
            self.ifs.update(self.mem, self.de)

            self.de.tick()

        # self.assertEqual(self.mem[0x80000000], self.de.ins)

class TestFull(unittest.TestCase):
    logging.basicConfig(filename='summary.log', filemode='w', level=logging.DEBUG)

    def setUp(self):
        self.mem = Mem()
        self.mem.memory = init_mem("rv32ui-p-add")
        self.ifs = InsFetch(self.mem.memory)
        self.de = Decode()
        self.ex = Execute()
        self.wb = Wb()
        # self.wb = Mock()
        # self.wb.wen = 0
        # self.wb.wdat = 0xabcd
        # self.wb.rd = 1

    
    def testUpdate(self):

        while(1):

            self.wb.update(self.mem)
            self.mem.update(self.ex)
            self.ex.update(self.de)
            self.de.update(self.ifs, self.wb)
            self.ifs.update(self.mem, self.de)

            self.wb.tick()
            self.mem.tick()
            self.ex.tick()
            self.de.tick()
            self.ifs.tick()
            logging.info("--"*32)

        # self.assertEqual(self.mem[0x80000000], self.de.ins)


if __name__ == '__main__':
    unittest.main(verbosity=2)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    # suite.addTest(TestExecute)
    # suite = unittest.TestSuite()
    # suite.addTest(TestUtils())
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)