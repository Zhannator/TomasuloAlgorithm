#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo RS

class RSobject:
    rs = {
        "int_adder_rs" : [],
        "fp_adder_rs" : [],
        "fp_multiplier_rs" : []
    }
    
    def rs_initialize(self, int_adder_num_rs, fp_adder_num_rs, fp_multiplier_num_rs):
        # initialize rs based on configs of FUs
        rs_entry = {
            "busy" : "no",
            "op" : "",
            "dest" : "",
            "vj" : 0,
            "vk" : 0,
            "qj" : "",
            "qk" : ""
        }
        for i in range(int_adder_num_rs):  
            self.rs["int_adder_rs"].append(rs_entry.copy())
        for i in range(fp_adder_num_rs):  
            self.rs["fp_adder_rs"].append(rs_entry.copy())
        for i in range(fp_multiplier_num_rs):  
            self.rs["fp_multiplier_rs"].append(rs_entry.copy())

    def rs_available(self, rs_name):
        # check rs to see if there is an open station, if yes - return index, if no, return -1
        for i, station in enumerate(self.rs[rs_name]):
            if station["busy"] == "no":
                return i
        return -1
        
    def rs_add(self, rs_name, i, op, dest, qj, qk):
        # add rs entry at index
        self.rs[rs_name][i]["busy"] = "yes"
        self.rs[rs_name][i]["op"] = op
        self.rs[rs_name][i]["dest"] = dest
        # need to check if we already have these values available
        self.rs[rs_name][i]["qj"] = qj
        self.rs[rs_name][i]["qk"] = qk
        # V2: don't forget to check for dependencies
        print("TODO")
        
    def rs_ready_to_execute(self):
        print "TODO"