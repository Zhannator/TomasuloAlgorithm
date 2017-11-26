#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo Load-Store Queue 
class LSQobject:
    lsq = []
    lsq_size = 0

    def lsq_initialize(self, num_load_store_rs):
        self.lsq_size = num_load_store_rs
    
    def lsq_available():
        if len(self.lsq) < lsq_size:
            return 1
        else:
            return -1
    
    def lsq_add(self, ls_instr, ls_constant, ls_addr_val, ls_addr_reg, store_val, store_reg, rob_dest):
        #add an entry in the queue if its not full:
        #    1) LOAD  -> addr (until EX stage) and value (until MEM stage unless forwarding) are NOT ready
        #    2) STORE -> addr (until EX stage) is NOT ready, value readiness depends on data dependencies
        #when a LOAD entry is added, run through queue to see if older STORE instr (with same addr) will forward
        #   -> which earlier STORE do I get my value from?

        if len(self.lsq) < num_load_store_rs:
            lsq_entry = { 
                "type" : ls_instr,    #Load or Store instruction (LD or SD)
                "dest" : rob_dest,   #rob entry destination
                "vj" : store_val,    #only used by store instruction for register that holds value to be stored in mem
                "qj" : store_reg,    #only used by store instruction for register that holds value to be stored in mem
                "vk" : ls_addr_val,    #Address register
                "qk" : ls_addr_reg,    #Address register dependency for V_k
                "constant" : ls_constant,
                "address" : "-",
                "value" : "-", #value brought back from memory if it's load instruction
                "fwd" : "-"}    #Set flag if forwarding used 
            self.lsq.append(lsq_entry.copy())
        else:
            print "Load-Store Queue full!"
            return -1
    
    def lsq_addr_reg_ready(self, rob_entry):
        for entry in self.lsq:
            if entry["dest"] == rob_entry:
                if entry["vk"] != "-":
                    return 1
                else:
                    return -1
 
    def lsq_get_address_values(self, rob_entry):
        for entry in self.lsq:
            if entry["dest"] == rob_entry:
                return [entry["constant"], entry["vk"]]
 
    def lsq_get_address(self, rob_entry):
        for entry in self.lsq:
            if entry["dest"] == rob_entry:
                return entry["address"]
 
    def lsq_pop(self):
        #pop the oldest instruction from the queue
        self.lsq.pop()
        print "TODO"

    def lsq_forwarding(self, rob_entry):
        # check if can forward a value to myself
        for index, entry in enumerate(self.lsq):
            if entry["dest"] == rob_entry:
                entry_index = index
                addr = entry["address"]
                break
        for index in range(entry_index - 1, 0, -1):
            if self.lsq[index]["type"] == "SD" and self.lsq[index]["address"] == addr:
                # forward if value is ready
                if self.lsq[index]["vj"] != "-":
                    self.lsq[entry_index]["value"] = self.lsq[index]["vj"]
                    self.lsq[entry_index]["fwd"] = 1
                    return 1
                break
        # if not return -1
        return -1