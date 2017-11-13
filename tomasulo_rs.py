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
            "op" : "-",
            "dest" : "-",
            "vj" : "-",
            "vk" : "-",
            "qj" : "-",
            "qk" : "-"
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
        
    def rs_add(self, rs_name, i, op, dest, vj, vk, qj, qk):
        # add rs entry at index
        self.rs[rs_name][i]["op"] = op
        self.rs[rs_name][i]["dest"] = dest
        self.rs[rs_name][i]["vj"] = vj
        self.rs[rs_name][i]["vk"] = vk
        self.rs[rs_name][i]["qj"] = qj
        self.rs[rs_name][i]["qk"] = qk
        if vj != "-" and vk != "-":
            self.rs[rs_name][i]["busy"] = "no"
        else:
            self.rs[rs_name][i]["busy"] = "yes"
    
    def rs_update_value():
        print "RS UPDATE VALUE TODO"
        
    def rs_get_values():
        print "RS GET VALUE TODO"
    
    def rs_ready_to_execute(self):
        # if busy == "no"
        print "RS READY TO EX TODO"
        
    def rs_print(self):
        print "###############################################################################################################################################################"
        print "{:^159}".format("INTEGER ADDER RS")
        print "###############################################################################################################################################################"    
        column_names = ["BUSY", "OP", "DEST", "Vj", "Vk", "Qj", "Qk"]
        row_format ="{:^10}" * len(column_names)
        print row_format.format(*column_names)
        for rs_entry in self.rs["int_adder_rs"]:
            rs_entry_list = [rs_entry["busy"], rs_entry["op"], rs_entry["dest"], rs_entry["vj"], rs_entry["vk"], rs_entry["qj"], rs_entry["qk"]]
            print row_format.format(*rs_entry_list)
        print   
        
        print "###############################################################################################################################################################"
        print "{:^159}".format("FLOATING POINT ADDER RS")
        print "###############################################################################################################################################################"    
        column_names = ["BUSY", "OP", "DEST", "Vj", "Vk", "Qj", "Qk"]
        row_format ="{:^10}" * len(column_names)
        print row_format.format(*column_names)
        for rs_entry in self.rs["fp_adder_rs"]:
            rs_entry_list = [rs_entry["busy"], rs_entry["op"], rs_entry["dest"], rs_entry["vj"], rs_entry["vk"], rs_entry["qj"], rs_entry["qk"]]
            print row_format.format(*rs_entry_list)
        print     
        
        print "###############################################################################################################################################################"
        print "{:^159}".format("FLOATING POINT MULTIPLIER RS")
        print "###############################################################################################################################################################"    
        column_names = ["BUSY", "OP", "DEST", "Vj", "Vk", "Qj", "Qk"]
        row_format ="{:^10}" * len(column_names)
        print row_format.format(*column_names)
        for rs_entry in self.rs["fp_multiplier_rs"]:
            rs_entry_list = [rs_entry["busy"], rs_entry["op"], rs_entry["dest"], rs_entry["vj"], rs_entry["vk"], rs_entry["qj"], rs_entry["qk"]]
            print row_format.format(*rs_entry_list)
        print