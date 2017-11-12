#!/usr/bin/python
# -*- coding: utf-8 -*-

# Tomasulo ROB

class ROBobject:
    rob = []
    rob_check_counter = 0 # rob check counter for checking to see if the top instruction is ready to commit
    rob_add_counter = 0 # rob pointer for where to add the next instruction in rob buffer

    def rob_initialize(self, num_rob_entries):
        # initialize rob
        rob_entry = { # needs to be initialized
        "busy" : "-",
        "instruction" : "-",
        "state" : "-",
        "destination" : "-", # “dest" field of a store instruction records its location in the load/store queue
        "value" : "-"
        }
        
        for i in range(num_rob_entries):
            self.rob.append(rob_entry.copy())
    
    def rob_instr_add(self, instruction):
        #add entry after you fetch instruction
        
        rob_dest = instruction.split()[1]
        
        if self.rob_add_counter < len(self.rob):
            self.rob[self.rob_add_counter]["destination"] = rob_dest
            self.rob_add_counter = self.rob_add_counter + 1; 
            
            #update the busy flag
            self.rob[self.rob_add_counter]["busy"] = "yes"
            
            #update the state
            
        else:
            print "ROB full!"
            return -1
        print rob
        print
    
    def rob_available(self):
        
        
    def rob_check_if_ready(self):
        #use busy flag to check if any entries are ready 
        #use counter for position in rob
        
        if self.rob[self.rob_check_counter]["busy"] == "no":
            print "rob" + str(self.rob_check_counter) + "is ready"
        
        if self.rob_check_counter == len(self.rob):
            self.rob_check_counter = 0
        else:
            self.rob_check_counter = self.rob_check_counter + 1
              
    def rob_update_value(self, dest_tag, rs_value):
        #use reservation stations to update rob when instructions have completed
        
        self.rob_update_index = int(dest_tag.split("ROB")[1])
        self.rob[self.rob_update_index]["value"] = rs_value
        
    def rob_update_state(self, dest_tag, rs_state):
        #use reservation stations to update rob state field
        
        self.rob_update_index = int(dest_tag.split("ROB")[1])
        self.rob[self.rob_update_index]["state"] = rs_state