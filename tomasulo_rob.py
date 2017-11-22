#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo ROB

class ROBobject:
    rob = []
    rob_check_counter = 0 # points to oldest/top instruction
    rob_add_counter = 0   # rob pointer for where to add the next instruction in rob buffer
    rob_total_entries = 0
    rob_empty_entry = {
        "busy" : "no",
        "instruction" : "-",
        "state" : "-", # possible states = ["ISSUE", "EX", "MEM", "WB", "COMMIT"]
        "destination" : "-", # “dest" field of a store instruction records its location in the load/store queue
        "value" : "-",
        "timing_table_entry_index" : "-"        # would like to have access to timing entry from here for convenience
    }
    def rob_initialize(self, num_rob_entries):
        # initialize rob

        for i in range(num_rob_entries):
            self.rob.append(self.rob_empty_entry.copy())
    
    def rob_instr_add(self, instruction, rob_dest, timing_table_entry_index):
        #add entry after you fetch instruction
        
        #rob_dest = instruction.split()[1] # destination register
        
        if self.rob_total_entries != len(self.rob): # if ROB isn't full
            # update ROB entry
            self.rob[self.rob_add_counter]["busy"] = "yes"
            self.rob[self.rob_add_counter]["instruction"] = instruction
            self.rob[self.rob_add_counter]["state"] = "ISSUE"
            self.rob[self.rob_add_counter]["destination"] = rob_dest # for l/s -> updated after execute stage; for branches -> "-"
            self.rob[self.rob_add_counter]["timing_table_entry_index"] = timing_table_entry_index
            return_value = "ROB" + str(self.rob_add_counter)
            # update counters for the next time
            if self.rob_add_counter + 1 == len(self.rob): # rotate ROB current entry counter
                self.rob_add_counter = 0
            else:
                self.rob_add_counter = self.rob_add_counter + 1 # point to the next entry to ROB 
            self.rob_total_entries = self.rob_total_entries + 1 # increment total number of entries 
            return return_value
        else:
            print "ROB full!"
            return -1 
    
    def rob_available(self):
        if self.rob_total_entries != len(self.rob):
            return 1
        else:
            return -1
    
    def rob_empty(self):
        # returns 1 if rob is empty
        if self.rob_total_entries == 0:
            return 1
        else:
            return -1
    
    def rob_check_if_ready_to_commit(self, rob_entry):
        #use busy flag to check if top entry is ready 
        #rob_check_counter points to the oldest/top instruction

        rob_index = int(rob_entry.split("ROB")[1])

        if rob_index == rob_check_counter and self.rob[self.rob_check_counter]["busy"] == "no":
            #if ready to commit -> clear entry and return [destination, value]
            print "rob" + str(self.rob_check_counter) + " is ready to commit"           
            return_value = [self.rob[self.rob_check_counter]["destination"], self.rob[self.rob_check_counter]["value"]]
            self.rob[self.rob_check_counter] = self.rob_empty_entry.copy()
            if self.rob_check_counter + 1 == len(self.rob): # rotate ROB top entry counter
                self.rob_check_counter = 0
            else:
                self.rob_check_counter = self.rob_check_counter + 1 # point to the next entry to ROB
            self.rob_total_entries = self.rob_empty_entry - 1
            return return_value
        else:
            return -1

    def rob_commit():
        self.rob[rob_check_counter] = self.rob_empty_entry.copy()
        if rob_check_counter + 1 == len(self.rob):
            rob_check_counter = 0
        else:
            rob_check_counter = rob_check_counter + 1
            
    def rob_get_instruction_id(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["instruction"].split(" ")[0]
            
    def rob_get_destination(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["destination"]
    
    def rob_get_value(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["value"]
    
    def rob_get_state(self, rob_entry):
        return self.rob[int(rob_entry.split("ROB")[1])]["state"]
            
    def rob_update_value(self, rob_entry, rs_value):
        #use reservation stations to update rob when instructions have completed
        rob_update_index = int(rob_entry.split("ROB")[1])
        self.rob[rob_update_index]["value"] = rs_value
        
    def rob_update_state(self, rob_entry, rs_state):
        #use reservation stations to update rob state field
        
        rob_update_index = int(rob_entry.split("ROB")[1])
        self.rob[rob_update_index]["state"] = rs_state
        
    def rob_get_tt_index(self, rob_entry):
        # return timing table index

        rob_update_index = int(rob_entry.split("ROB")[1])
        return self.rob[rob_update_index]["timing_table_entry_index"]        

    def rob_head_node(self, instruction_issue_indicator):
        # return the first entry in rob table, -1 if rob table is empty
        if self.rob_add_counter == 0:
            rob_add_counter_previous = len(self.rob) - 1
        else:
            rob_add_counter_previous = self.rob_add_counter - 1
        if (self.rob_check_counter == self.rob_add_counter) or (instruction_issue_indicator != "-" and self.rob_check_counter == rob_add_counter_previous): #returns -1 if there ROB is empty
            return -1
        else:
            return "ROB" + str(self.rob_check_counter)
        
    def rob_next(self, rob_entry, instruction_issue_indicator):
        # if rob_entry = ROB1, rob_next will return ROB2 if this entry is occupied
        rob_index = int(rob_entry.split("ROB")[1])
        if rob_index == len(self.rob) - 1: # rotate ROB current entry counter
                rob_index = 0
        else:
            rob_index = rob_index + 1
        
        
        if self.rob_add_counter == 0:
            rob_add_counter_previous = len(self.rob) - 1
        else:
            rob_add_counter_previous = self.rob_add_counter - 1
        
        if (rob_index == self.rob_add_counter) or (instruction_issue_indicator != "-" and rob_index == rob_add_counter_previous): #returns -1 if there is no more ROB entries
            return -1
        else:
            return "ROB" + str(rob_index)
    
    def rob_print(self):
        print "###############################################################################################################################################################"
        print "{:^159}".format("ROB")
        print "###############################################################################################################################################################"    
        column_names = ["", "BUSY", "INSTRUCTION", "STATE", "DESTINATION", "VALUE"]
        row_format ="{:^16}" * len(column_names)
        print row_format.format(*column_names)
        for index, rob_entry in enumerate(self.rob):
            rob_entry_list = ["ROB"+str(index), rob_entry["busy"], rob_entry["instruction"], rob_entry["state"], rob_entry["destination"], rob_entry["value"]]
            print row_format.format(*rob_entry_list)
        print   