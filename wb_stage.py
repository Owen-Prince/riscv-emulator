class Wb():
    def __init__(self):
        self.rd = 0
        self.wen = False
        self.wdat = 0x0

    def update(self, mem):
        self.rd = mem.rd
        self.wen = mem.wen
        self.wdat = mem.wdat

    def tick(self):
        pass