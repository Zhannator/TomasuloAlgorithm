#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo RS

class RSobject:
    rs = {
        "int_adder_rs" : [],
        "fp_adder_rs" : [],
        "fp_multiplier_rs" : []
    }
    int_adder_rs_size = 0
    fp_adder_rs_size = 0
    fp_multiplier_rs_size = 0
    rs_entry = {
		"busy" : "no",
		"op" : "-",
		"dest" : "-",
		"vj" : "-",
		"vk" : "-",
		"qj" : "-",
		"qk" : "-"
	}
	
	#self.rs["int_adder_rs"].append(self.rs_entry.copy())
	#self.rs["fp_adder_rs"].append(self.rs_entry.copy())
    
    def rs_initialize(self, int_adder_num_rs, fp_adder_num_rs, fp_multiplier_num_rs):
        # initialize rs based on configs of FUs
        self.int_adder_rs_size = int_adder_num_rs
        self.fp_adder_rs_size = fp_adder_num_rs
        self.fp_multiplier_rs_size = fp_multiplier_num_rs

    def rs_available(self, rs_name):
        # check rs to see if there is an open station, if yes - return 1, if no, return -1
        if (rs_name == "int_adder_rs" and len(self.rs[rs_name]) < self.int_adder_rs_size) or (rs_name == "fp_adder_rs" and len(self.rs[rs_name]) < self.fp_adder_rs_size) or (rs_name == "fp_multiplier_rs" and len(self.rs[rs_name]) < self.fp_multiplier_rs_size):
            return 1
        return -1
        
    def rs_add(self, rs_name, op, dest, vj, vk, qj, qk):
        # add rs entry
        if (rs_name == "int_adder_rs" and len(self.rs[rs_name]) < self.int_adder_rs_size) or (rs_name == "fp_adder_rs" and len(self.rs[rs_name]) < self.fp_adder_rs_size) or (rs_name == "fp_multiplier_rs" and len(self.rs[rs_name]) < self.fp_multiplier_rs_size):
            if vj != "-" and vk != "-":
                busy = "no"
            else:
                busy = "yes"
            rs_entry = {
                "busy" : busy,
                "op" : op,
                "dest" : dest,
                "vj" : vj,
                "vk" : vk,
                "qj" : qj,
                "qk" : qk
            }
            self.rs[rs_name].append(rs_entry.copy())
        else:
            return -1
            
    def rs_no_dependencies(self, rs_name, rob_entry):
		#returns 1 if all the values are ready and the instruction is ready to execute
		for rs_entry in self.rs[rs_name]:
			if rs_entry["dest"] == rob_entry:
				if rs_entry["busy"] == "no":
					return 1
				else:
					return -1
		return -1
	
    def rs_update_value(self, destination, value):
        # find all the rs entries that use this rob entry as a place holder and update items
        for rs_name in ["int_adder_rs", "fp_adder_rs", "fp_multiplier_rs"]:
            for entry in self.rs[rs_name]:
                # check qj and qk
                if entry["qj"] == destination:
                    entry["qj"] = "-"
                    entry["vj"] = value
                if entry["qk"] == destination:
                    entry["qk"] = "-"
                    entry["vk"] = value
                if entry["qj"] == "-" and entry["qk"] == "-":
                    entry["busy"] = "no"
        
    def rs_get_values(self, rs_name, rob_entry):
		#returns [vj, vk]
		for rs_entry in self.rs[rs_name]:
			if rs_entry["dest"] == rob_entry:
				return [rs_entry["vj"], rs_entry["vk"]]
		return -1		
        
    def rs_clear_entry(self, rob_entry):
        for rs_name in ["int_adder_rs", "fp_adder_rs", "fp_multiplier_rs"]:
            for index, rs_entry in enumerate(self.rs[rs_name]):
                if rs_entry["dest"] == rob_entry:
                    del self.rs[rs_name][index]
                    return
                
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