#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo TIMING TABLE

class TTobject:
    timing_table = []

    def timing_table_add(self, PC, instruction, clock_cycle):
        timing_table_entry = {
            "PC" : PC,
            "instruction" : instruction,
            "ISSUE" : clock_cycle,
            "EX_START" : "-",
            "EX_FINISH" : "-",
            "MEM_START" : "-",
            "MEM_FINISH" : "-",      
            "WB" : "-",
            "COMMIT_START" : "-",
            "COMMIT_FINISH" : "-"
        }
        self.timing_table.append(timing_table_entry.copy())

    def timing_table_update(self, tt_entry_index, state, current_cycle, num_of_op_cycles):
        if state == "MEM" or state == "EX" or state == "COMMIT":
            self.timing_table[tt_entry_index][state + "_START"] = current_cycle
            self.timing_table[tt_entry_index][state + "_FINISH"] = current_cycle + num_of_op_cycles - 1
        else:
            self.timing_table[tt_entry_index][state] = current_cycle
            
    def timing_table_check_if_done(self, tt_entry_index, state, current_cycle):
        if current_cycle > self.timing_table[tt_entry_index][state + "_FINISH"]:
            return 1
        else:
            return -1
        
    def time_table_print(self):
        print "###############################################################################################################################################################"
        print "{:^159}".format("TIMING TABLE")
        print "###############################################################################################################################################################"    
        column_names = [ "PC", "INSTRUCTION", "ISSUE", "EX_S", "EX_F", "MEM_S", "MEM_F", "WB", "COMMIT_S", "COMMIT_F"]
        row_format ="{:^16}" * len(column_names)
        print row_format.format(*column_names)
        for tt_entry in self.timing_table:
            tt_entry_list = [tt_entry["PC"], tt_entry["instruction"], tt_entry["ISSUE"], tt_entry["EX_START"], tt_entry["EX_FINISH"], tt_entry["MEM_START"], tt_entry["MEM_FINISH"], tt_entry["WB"], tt_entry["COMMIT_START"], tt_entry["COMMIT_FINISH"]]
            print row_format.format(*tt_entry_list)
        print