from typing import Dict
from Instruction import Instruction


class ForwardingUnit:
    """
    Represent destination data as a list of dicts 
    of rd : wdat.
    build_index does a hash of the list of dicts 
    """
    def __init__(self):
        self.data = []
        self.index = {}
        
    def insert(self, ins: Instruction)->None:
        """
        Append dict of rd : val to the queue. 
        """
        if ins.wen:
            self.data.append({'rd' : ins.rd, 'wdat' : ins.wdat})

    def build_index(self)->Dict:
        """hash the list, give the later entried priority"""
        index = {}
        for i in self.data:
            index[i['rd']] = i['wdat']
        return index

    def forward(self, ins: Instruction)->Instruction:
        """
        1. take original instruction, determine if values need to be forwarded
        2. modify the values of rdat1 and rdat2 if necessary
        3. return the new instruction 
        """
        index = self.build_index()
        ins.rdat1 = index[ins.rs1] if ins.rs1 in index else ins.rdat1
        ins.rdat2 = index[ins.rs2] if ins.rs2 in index else ins.rdat2
        ins.set_control_signals(ins.pc)
        return ins

    def pop(self)->None:
        """pop front of queue"""
        if len(self.data) > 0:
            self.data.pop()

    def __str__(self):
        as_string = ""
        index = self.build_index()
        # return ""
        if not index:
            return ""
        for k in index.keys():
            as_string = as_string + f"x{k}: {index[k]}   "
        return as_string