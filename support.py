import struct
import binascii

from elftools.elf.elffile import ELFFile

from cpu_types import Aluop, Funct3, Ops, get_aluop_d, get_opname, gib, pad, sign_extend, unsigned, zext
from stages import Decode, Execute, Fetch, Memory, Writeback




