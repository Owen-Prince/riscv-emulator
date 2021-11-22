from cpu_types import Ops


class Forwarding_Unit():
    def __init__(self):
        self.rd_lookup = {
            "de"  : [], 
            "ex"  : [], 
            "mem" : [], 
            "wb"  : [], 
        }
        self.rs_lookup = {
            "de"  : [], 
            "ex"  : [], 
            "mem" : [], 
            "wb"  : [], 
        }
        #forward enable
        self.f_en = {
            "de"  : False,
            "ex"  : False, 
            "mem" : False,
        }
        self.stall = {
            "ifs" : False,
            "de"  : False,
            "ex"  : False,
            "mem" : False,
            "wb"  : False,
        }
        self.flush = {
            "ifs" : False,
            "de"  : False,
            "ex"  : False,
            "mem" : False,
            "wb"  : False,
        }


    def update(self, ifs, de, ex, mem, wb):
        
        self.rd_lookup = {
            "de"  : de.rd,
            "ex"  : ex.rd,
            "mem" : mem.rd,
            "wb"  : wb.rd,
        }

        self.rs_lookup = {
            "de"  : [de.rs1,  de.rs2],
            "ex"  : [ex.rs1,  ex.rs2],
            "mem" : [mem.rs1, mem.rs2],
            "wb"  : [wb.rs1,  wb.rs2],
        }

        self.f_en = {
            "de"    : self.rd_lookup['ex']  in self.rs_lookup['de'],
            "ex"    : self.rd_lookup['mem'] in self.rs_lookup['ex'],
            "mem"   : self.rd_lookup['wb']  in self.rs_lookup['mem'],
        }

        self.flush['ifs'] = de.opcode in [ Ops.JAL, Ops.JALR] or (de.opcode == Ops.BRANCH and de.mispredict == True)


        