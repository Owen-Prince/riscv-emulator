from stages import *
import logging
import os
from elftools.elf.elffile import ELFFile

from support import Ram

# from stages import *
FORMAT = '%(message)s'

logging.basicConfig(filename='summary.log', format=FORMAT, filemode='w', level=logging.INFO)
logging.info("%s", f"{f'Stage':10}-- ({f'PC':8})")
logging.info("%s", "-" * 23)
ram = Ram()


s5 = Writeback()
s4 = Memory()
s3 = Execute()
s2 = Decode()
s1 = Fetch(ram)

fwd = {}

# for i in range(35):
def step():
    global s1, s2, s3, s4, s5, fwd, ram
    s2.wb(prev=s5)
    fwd['w'] = s5.tick(s4)
    fwd['m'] = s4.tick(s3)
    fwd['e'] = s3.tick(s2)
    fwd['d'] = s2.tick(s1)
    s1.tick(decode=s2)
    print(fwd)

# print(s2.regs)

if __name__ == "__main__":
    # global ram
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    # for filename in glob.glob("riscv-tests/isa/rv32ui-p-*"):
    filename = "riscv-tests/isa/rv32ui-p-add"
    # if x.endswith('.dump'):
        # continue
    ram.load(filename)
    inscnt = 0
    s1.ins_hex = s1.fetch(s1.pc)

    # while step():
    logging.info("%s", f"CLK CYCLE : {inscnt} {f'-'*24}")
    while inscnt < 90:
        step()
        inscnt += 1
        logging.info("%s", f"CLK CYCLE : {inscnt} {f'-'*24}")
    # logging.debug("  ran %d instructions" % inscnt)
    # logging.debug(str(ram.csrs))
    print(s2.regs)
    # print(ram)