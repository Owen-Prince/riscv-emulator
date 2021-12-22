import glob
import logging
import os
from typing import List
from cpu_types import Fail, Success

from datapath import Datapath

FORMAT = '%(message)s'

logging.basicConfig(filename='trace.log', format=FORMAT, filemode='w', level=logging.INFO)
logging.info("%s", f"{f'Stage':10}-- ({f'PC':8})")
logging.info("%s", "-" * 23)

def riscv_tests_exit(wdat) -> None:
    """
    For the riscv-tests repository, exit if there's an ecall and
    the value of register 3 in the reg file is >= 1.
    mret happens when the value in the register file is 0; since 
    the privileged ISA is not implemented yet, this is a temporary 
    measure to just ignore that instruction.
    The test is successful if the value in x3 == 1, else if it's
    greater than 1 then something went wrong
    """
    if wdat > 1:
        raise Fail
    elif wdat == 1:
        raise Success

def get_test_files() -> List:
    """subfolder of riscv-tests/isa/"""
    return glob.glob("riscv-tests/isa/rv32ui-p-*")

if __name__ == "__main__":
    # global ram
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    filename_list = get_test_files()
    for filename in filename_list:
        if filename.endswith('.dump'):
            continue
        # IF using the riscv_test repository, use riscv_tests_exit
        datapath = Datapath(riscv_tests_exit, 0x80000000)
        datapath.run(filename)
        