class Forwarding_Unit():
    def __init__(self):
        self.rd_lookup = {
            "de"  : [], 
            "ex"  : [], 
            "mem" : [], 
            "wb"  : [], 
        }
        self.rs1_lookup = {
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
        
        self.rd_lookup['de'] = {
            "de"  : de.rd,
            "ex"  : ex.rd,
            "mem" : mem.rd,
            "wb"  : wb.rd,
        }
        de.rd
        self.rd_lookup['de'] = de.rd
        self.rd_lookup['de'] = de.rd
        self.rd_lookup['de'] = de.rd

    def tick(self):

        