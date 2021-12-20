from cpu_types import Ops
from stages import Decode, Execute, Fetch, Memory, Writeback


class HazardUnit():
    def __init__(self, f: Fetch, d: Decode, e: Execute, m: Memory, w: Writeback):

        self.f = f
        self.d = d
        self.e = e
        self.m = m

        self.stall_f = self.f.busy
        self.stall_d = self.d.busy
        self.stall_e = self.e.busy
        self.stall_m = self.m.busy

        self.load_use()
        self.stall_prev_stages()


    def load_use(self) -> None:
        """
        Load in mem stage:
            ex-mem
            de-mem
        Load in Ex stage:
            de-ex
        """
        if self.m.ins.opcode == Ops.LOAD:
            rd = self.m.ins.rd
            if self.e.ins.rs1 == rd or self.e.ins.rs2 == rd:
                self.stall_e = True
            if self.d.ins.rs1 == rd or self.d.ins.rs2 == rd:
                self.stall_d = True
        if self.e.ins.opcode == Ops.LOAD:
            rd = self.e.ins.rd
            if self.d.ins.rs1 == rd or self.d.ins.rs2 == rd:
                self.stall_d = True

    def stall_prev_stages(self) -> None:
        """
        Stall all previous stages
        """
        if self.stall_m:
            self.stall_e = True
        if self.stall_e:
            self.stall_d = True
        if self.stall_d:
            self.stall_f = True
