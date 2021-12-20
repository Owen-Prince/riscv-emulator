import glob
import logging
import os
from cpu_types import Fail, Success

from datapath import Datapath

FORMAT = '%(message)s'

logging.basicConfig(filename='trace.log', format=FORMAT, filemode='w', level=logging.INFO)
logging.info("%s", f"{f'Stage':10}-- ({f'PC':8})")
logging.info("%s", "-" * 23)

def riscv_tests_exit(wdat):
    if wdat > 1:
        raise Fail
    elif wdat == 1:
        raise Success

def get_test_files():
    """subfolder of riscv-tests/isa/"""
    return glob.glob("riscv-tests/isa/")

if __name__ == "__main__":
    # global ram
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    # filename_list = get_test_files()
    filename_list = []
    filename_list.append("riscv-tests/isa/rv32ui-p-jal")
    for filename in filename_list:
        if filename.endswith('.dump'):
            continue
        datapath = Datapath(riscv_tests_exit)
        datapath.run(filename)
        