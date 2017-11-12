#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo TIMING TABLE

class TTobject:
    timing_table = []

    def timing_table_add(self, PC, instruction, clock_cycle):
        timing_table_entry = {
            "PC" : PC,
            "instruction" : instruction,
            "issue" : clock_cycle,
            "ex_start" : "-",
            "ex_finish" : "-",
            "mem_start" : "-",
            "mem_finish" : "-",      
            "wb" : "-",
            "commit_start" : "-",
            "commit_finish" : "-"
        }
        self.timing_table.append(timing_table_entry.copy())

    def timing_table_update(self):
        print "TIMING TABLE UPDATE TODO"
        
    def time_table_print(self):
        print "###############################################################################################################################################################"
        print "{:^159}".format("TIMING TABLE")
        print "###############################################################################################################################################################"    
        column_names = [ "PC", "INSTRUCTION", "ISSUE", "EX_S", "EX_F", "MEM_S", "MEM_F", "WB", "COMMIT_S", "COMMIT_F"]
        row_format ="{:^16}" * len(column_names)
        print row_format.format(*column_names)
        for tt_entry in self.timing_table:
            tt_entry_list = np.array([tt_entry["PC"], tt_entry["instruction"], tt_entry["issue"], tt_entry["ex_start"], tt_entry["ex_finish"], tt_entry["mem_start"], tt_entry["mem_finish"], tt_entry["wb"], tt_entry["commit_start"], tt_entry["commit_finish"]])
            print row_format.format(*tt_entry_list)
        print