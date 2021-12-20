# from _typeshed import Self
import binascii
import struct

from elftools.elf.elffile import ELFFile

from cpu_types import pad


class Ram():
    def __init__(self):
        self.size = 0x4000
        self.memory = b'\x00'*self.size
        print(len(self.memory))

    def __getitem__(self, key):
        key -= 0x80000000
        if key < 0 or key >= len(self.memory):

            raise Exception("mem fetch to %x failed" % key)
        assert key >=0 and key < len(self.memory)
        return struct.unpack("<I", self.memory[key:key+4])[0]

    def __setitem__(self, key, val):
        key -= 0x80000000
        # if not (key >=0 and key < len(self.memory)): 
        #     print(f"{key + 0x80000000:x}")
        assert key >=0 and key < len(self.memory)
        # print(struct.pack("I", val))
        self.memory = self.memory[:key] + val + self.memory[key+len(val):]

    def load(self, filename):
        self.reset()
        with open(filename, 'rb') as f:
            e = ELFFile(f)
            for s in e.iter_segments():
                # if s.data() != 0:
                    # print(s.data(), "\n")
                self[s.header.p_paddr] = s.data()
            with open("test-cache/%s" % filename.split("/")[-1], "wb") as g:
                g.write(b'\n'.join([binascii.hexlify(self.memory[i:i+4][::-1]) for i in range(0,len(self.memory),4)]))
    def reset(self):
        self.memory =  b'\x00'*0x4000
    def update(self, ram):
        for i in range(self.size // 4):
            self.memory[i] = ram.memory[i]
        # self.memory = ram.memory 

    def __str__(self):
        s = []
        bad = []
        for i in range(0, len(self.memory), 4):
            if self[i + 0x80000000] != 0:
                padded = pad(hex(self[i + 0x80000000])[2:])
                if len(padded) != 8: bad.append(hex(self[i + 0x80000000]))
                s.append(f"{hex(i)}:\t0x{padded}\n")
        return "".join(s)
