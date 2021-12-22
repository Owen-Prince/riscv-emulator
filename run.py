import logging
import os
import sys
from cpu_types import Fail, Success

from datapath import Datapath

FORMAT = '%(message)s'

logging.basicConfig(filename='trace.log', format=FORMAT, filemode='w', level=logging.INFO)
logging.info("%s", f"{f'Stage':10}-- ({f'PC':8})")
logging.info("%s", "-" * 23)

def test_exit(wdat) -> None:
    """
    Use this function for testing files that are not riscv-tests 
    unit test files.
    When a test succeeds, it will throw an exception of type "success"
    that is then caught by the datapath class
    When a test fails, it will throw an exception of type "fail" which
    will not be caught by datapath class
    """
    if wdat != 1:
        raise Fail
    elif wdat == 1:
        raise Success


if __name__ == "__main__":
    # global ram
    if not os.path.isdir('test-cache'):
        os.mkdir('test-cache')
    filename = sys.argv[1]
    datapath = Datapath(test_exit, 0x80000000)
    datapath.run(filename)
        