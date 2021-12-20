from Instruction import Instruction
from stages import Stage


class ForwardingUnit:
    """
    Represent destination data as a list of dicts 
    of rd : wdat.
    build_index does a hash of the list of dicts 
    """
    def __init__(self):
        self.data = []
        self.index = {}
        
    def insert(self, ins: Instruction):
        """
        Append dict of rd : val to the queue. 
        """
        if ins.wen:
            self.data.append({'rd' : ins.rd, 'wdat' : ins.wdat})

    def build_index(self):
        """hash the list, give the later entried priority"""
        index = {}
        for i in self.data:
            index[i['rd']] = i['wdat']
        return index

    def forward(self, rs1, rs2):
        """
        return rs1, rs2
        rs1 : forwarded value of rs1
        """
        index = self.build_index()
        # print(index)
        rs1_fwd = index[rs1] if rs1 in index else None
        rs2_fwd = index[rs2] if rs2 in index else None
        print(index)
        return rs1_fwd, rs2_fwd

    def pop(self):
        """pop front of queue"""
        if len(self.data) > 0:
            self.data.pop()

    def __str__(self):
        as_string = ""
        self.build_index()
        print(self.data)
        return ""
        for k in self.index.keys():
            as_string = as_string + f"x{k}: {self.data[k]}  "
        return as_string