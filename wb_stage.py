import logging
from PipelineStage import PipelineStage

class Wb(PipelineStage):
    def __init__(self):
        super().__init__()
        self.rd = 0
        self.wen = False
        self.wdat = 0x0

    def update(self, mem):
        super().update(mem)
        self.rd = mem.rd
        self.wen = mem.wen
        self.wdat = mem.wdat
        logging.info("WRITEBACK: %s", self)

    def tick(self):
        if self.ins == -1: return
        pass