import logging
import os

import glob
from stages import Decode, Execute, Fetch, Memory, Writeback
from support import ForwardingUnit, Ram, Success

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


def step():
    fwd = ForwardingUnit()
    try:
        s2.wb(prev=s5)
        s5.tick(s4)
        fwd[s5.ins.rd] = s5.ins.wdat
        s4.tick(s3)
        fwd[s4.ins.rd] = s4.ins.wdat
        s3.tick(s2)
        fwd[s3.ins.rd] = s3.ins.wdat
        s2.tick(s1)
        s1.tick(decode=s2)
        print(fwd)
    except Success:
        return False
    except Exception as e:
        print("Error", repr(e))
        raise
    return True

def get_test_files():
    """subfolder of riscv-tests/isa/"""
    return glob.glob("riscv-tests/isa/")

if __name__ == "__main__":
    # global ram
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    # filename_list = get_test_files()
    # filename = "riscv-tests/isa/rv32ui-p-add"
    filename_list = []
    for filename in filename_list:
        if filename.endswith('.dump'):
            continue

        ram.load(filename)
        
        inscnt = 0
        s1.ins_hex = s1.fetch(s1.pc)

        # while step():
        logging.info("%s", f"CLK CYCLE : {inscnt} {f'-'*24}")
        while inscnt < 10:
            step()
        # while(step()):
            inscnt += 1
            logging.info("%s", f"CLK CYCLE : {inscnt} {f'-'*24}")
        # logging.debug("  ran %d instructions" % inscnt)
        # logging.debug(str(ram.csrs))
        print(s2.regs)
